from datetime import datetime

import bcrypt
from mysql.connector import Error, IntegrityError

from data.conexion import obtener_conexion
from logic.validaciones import dni_valido, limpiar_dni, telefono_valido


def _normalizar_rol(rol):
    roles = {
        "administrador": "Administrador",
        "gerente": "Gerente",
        "supervisor": "Supervisor",
        "cajero": "Cajero",
        "repositor": "Repositor",
        "vendedor": "Vendedor"
    }
    return roles.get(str(rol).casefold(), str(rol))


class RepositorioMySQL:
    """Persistencia de clientes, empleados, categorías y ventas."""

    def _consultar(self, sql, parametros=()):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def _ejecutar(self, sql, parametros=()):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)
            conexion.commit()
            return cursor.lastrowid
        except Error:
            if conexion and conexion.is_connected():
                conexion.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def listar_categorias(self):
        return [
            {"id": fila[0], "nombre": fila[1]}
            for fila in self._consultar(
                "SELECT id_categoria, nombre FROM categorias ORDER BY nombre"
            )
        ]

    def guardar_categoria(self, categoria):
        if categoria.get("id"):
            self._ejecutar(
                "UPDATE categorias SET nombre = %s WHERE id_categoria = %s",
                (categoria["nombre"].strip(), categoria["id"])
            )
            return categoria["id"]
        return self._ejecutar(
            "INSERT INTO categorias (nombre) VALUES (%s)",
            (categoria["nombre"].strip(),)
        )

    def eliminar_categoria(self, id_categoria):
        self._ejecutar(
            "DELETE FROM categorias WHERE id_categoria = %s",
            (id_categoria,)
        )

    def listar_clientes(self):
        filas = self._consultar(
            """SELECT c.id_cliente, c.nombre, c.apellido, c.dni, c.telefono,
                      COUNT(v.id_venta)
               FROM clientes c
               LEFT JOIN ventas v ON v.id_cliente = c.id_cliente
               GROUP BY c.id_cliente, c.nombre, c.apellido, c.dni, c.telefono
               ORDER BY c.nombre, c.apellido, c.id_cliente"""
        )
        return [
            {
                "id": fila[0],
                "nombre": fila[1],
                "apellido": fila[2] or "",
                "dni": fila[3] or "",
                "telefono": fila[4] or "",
                "cantidad_ventas": fila[5],
                "historial_compras": []
            }
            for fila in filas
        ]

    def guardar_cliente(self, cliente):
        nombre = cliente.nombre.strip()
        apellido = cliente.apellido.strip()
        dni = limpiar_dni(cliente.dni) or None
        telefono = cliente.telefono.strip() or None
        if not nombre:
            raise ValueError("El nombre del cliente es obligatorio.")
        if len(nombre) > 60 or len(apellido) > 60:
            raise ValueError("El nombre y apellido admiten hasta 60 caracteres.")
        if dni and (len(dni) > 60 or not dni_valido(dni)):
            raise ValueError("El DNI debe tener 7 u 8 números.")
        if telefono and (len(telefono) > 20 or not telefono_valido(telefono)):
            raise ValueError("El teléfono contiene caracteres no permitidos.")
        try:
            if cliente.id > 0:
                self._ejecutar(
                    """UPDATE clientes
                       SET nombre = %s, apellido = %s, dni = %s, telefono = %s
                       WHERE id_cliente = %s""",
                    (nombre, apellido, dni, telefono, cliente.id)
                )
                return cliente.id
            cliente.id = self._ejecutar(
                """INSERT INTO clientes (nombre, apellido, dni, telefono)
                   VALUES (%s, %s, %s, %s)""",
                (nombre, apellido, dni, telefono)
            )
        except IntegrityError as error:
            if error.errno == 1062:
                raise ValueError(
                    "Ya existe un cliente registrado con ese DNI."
                ) from error
            raise
        return cliente.id

    def eliminar_cliente(self, id_cliente):
        self._ejecutar(
            "DELETE FROM clientes WHERE id_cliente = %s",
            (id_cliente,)
        )

    def listar_empleados(self):
        return [
            {
                "id": fila[0],
                "nombre": f"{fila[1]} {fila[2]}".strip(),
                "dni": "",
                "rol": _normalizar_rol(fila[4]),
                "usuario": fila[3],
                "activo": bool(fila[5])
            }
            for fila in self._consultar(
                """SELECT id_empleado, nombre, apellido, usuario, rol, activo
                   FROM empleados ORDER BY nombre, apellido"""
            )
        ]

    def autenticar_empleado(self, usuario, clave):
        filas = self._consultar(
            """SELECT id_empleado, nombre, apellido, usuario, rol, clave, activo
               FROM empleados WHERE usuario = %s""",
            (usuario,)
        )
        if not filas:
            return None
        fila = filas[0]
        hash_clave = fila[5]
        if not isinstance(hash_clave, str) or not hash_clave:
            return None
        try:
            valida = bcrypt.checkpw(
                clave.encode("utf-8"),
                hash_clave.encode("ascii")
            )
        except (ValueError, TypeError):
            valida = False
        if not valida and not hash_clave.startswith(("$2a$", "$2b$", "$2y$")):
            valida = hash_clave == clave
            if valida:
                nuevo_hash = bcrypt.hashpw(
                    clave.encode("utf-8"), bcrypt.gensalt()
                ).decode("ascii")
                self._ejecutar(
                    "UPDATE empleados SET clave = %s WHERE id_empleado = %s",
                    (nuevo_hash, fila[0])
                )
        if not valida or not fila[6]:
            return None
        return {
            "id": fila[0],
            "nombre": f"{fila[1]} {fila[2]}".strip(),
            "dni": "",
            "rol": _normalizar_rol(fila[4]),
            "usuario": fila[3],
            "activo": bool(fila[6])
        }

    def guardar_empleado(self, empleado, clave=None):
        nombre_completo = empleado.get("nombre")
        usuario = empleado.get("usuario")
        rol = empleado.get("rol")
        if not all(isinstance(valor, str) for valor in (nombre_completo, usuario, rol)):
            raise ValueError("Nombre, usuario y rol deben ser texto.")
        partes_nombre = nombre_completo.strip().split(maxsplit=1)
        nombre = partes_nombre[0] if partes_nombre else ""
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
        usuario = usuario.strip()
        rol = rol.strip()
        if not nombre or len(nombre) > 60:
            raise ValueError("El nombre es obligatorio y admite hasta 60 caracteres.")
        if len(apellido) > 60:
            raise ValueError("El apellido admite hasta 60 caracteres.")
        if not usuario or len(usuario) > 30:
            raise ValueError("El usuario es obligatorio y admite hasta 30 caracteres.")
        if not rol or len(rol) > 20:
            raise ValueError("El rol es obligatorio y admite hasta 20 caracteres.")
        if not empleado.get("id") and clave is None:
            raise ValueError("La contraseña es obligatoria para un empleado nuevo.")
        if clave is not None and (
            not isinstance(clave, str)
            or len(clave) < 12
            or len(clave.encode("utf-8")) > 72
        ):
            raise ValueError(
                "La contraseña debe tener al menos 12 caracteres "
                "y no superar 72 bytes UTF-8."
            )
        parametros = (
            nombre, apellido, usuario, rol.casefold(),
            int(bool(empleado.get("activo", True)))
        )
        if empleado.get("id"):
            if clave:
                hash_clave = bcrypt.hashpw(
                    clave.encode("utf-8"), bcrypt.gensalt()
                ).decode("ascii")
                self._ejecutar(
                    """UPDATE empleados
                       SET nombre = %s, apellido = %s, usuario = %s, rol = %s,
                           activo = %s, clave = %s
                       WHERE id_empleado = %s""",
                    (*parametros, hash_clave, empleado["id"])
                )
            else:
                self._ejecutar(
                    """UPDATE empleados
                       SET nombre = %s, apellido = %s, usuario = %s, rol = %s,
                           activo = %s
                       WHERE id_empleado = %s""",
                    (*parametros, empleado["id"])
                )
            return empleado["id"]
        hash_clave = bcrypt.hashpw(
            clave.encode("utf-8"), bcrypt.gensalt()
        ).decode("ascii")
        return self._ejecutar(
            """INSERT INTO empleados
               (nombre, apellido, usuario, rol, clave, activo)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                parametros[0], parametros[1], parametros[2], parametros[3],
                hash_clave, parametros[4]
            )
        )

    def eliminar_empleado(self, id_empleado):
        self._ejecutar(
            "DELETE FROM empleados WHERE id_empleado = %s",
            (id_empleado,)
        )

    def listar_ventas(self):
        ventas = self._consultar(
            """SELECT v.id_venta, v.fecha, v.total, v.metodo_pago,
                      v.id_cliente, c.nombre, c.apellido,
                      v.id_empleado, e.nombre, e.apellido
               FROM ventas v
               LEFT JOIN clientes c ON c.id_cliente = v.id_cliente
               LEFT JOIN empleados e ON e.id_empleado = v.id_empleado
               ORDER BY v.id_venta"""
        )
        resultado = []
        for fila in ventas:
            detalles = self._consultar(
                """SELECT d.id_producto, p.nombre, d.cantidad,
                          d.precio_unitario
                   FROM detalle_venta d
                   JOIN productos p ON p.id_producto = d.id_producto
                   WHERE d.id_venta = %s ORDER BY d.id_detalle""",
                (fila[0],)
            )
            resultado.append({
                "id": fila[0],
                "fecha": fila[1].strftime("%d/%m/%Y %H:%M"),
                "total": float(fila[2]),
                "metodo_pago": fila[3],
                "cliente_id": fila[4],
                "cliente_nombre": " ".join(
                    parte for parte in (fila[5], fila[6]) if parte
                ) or "Cliente General",
                "empleado_id": fila[7],
                "empleado_nombre": " ".join(
                    parte for parte in (fila[8], fila[9]) if parte
                ),
                "productos": [
                    {
                        "id": item[0],
                        "nombre": item[1],
                        "cantidad": item[2],
                        "precio": float(item[3]),
                        "subtotal": float(item[3]) * item[2]
                    }
                    for item in detalles
                ]
            })
        return resultado

    def registrar_venta(self, carrito, cliente_id, empleado_id, metodo_pago):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            total = sum(
                float(item["producto"].precio) * item["cantidad"]
                for item in carrito.items
            )
            cursor.execute(
                """INSERT INTO ventas
                   (total, metodo_pago, id_cliente, id_empleado)
                   VALUES (%s, %s, %s, %s)""",
                (total, metodo_pago, cliente_id, empleado_id)
            )
            id_venta = cursor.lastrowid
            for item in carrito.items:
                producto = item["producto"]
                cantidad = item["cantidad"]
                cursor.execute(
                    """UPDATE productos SET stock = stock - %s
                       WHERE id_producto = %s AND stock >= %s""",
                    (cantidad, producto.id, cantidad)
                )
                if cursor.rowcount != 1:
                    raise ValueError(
                        f"No hay stock suficiente de {producto.nombre}."
                    )
                cursor.execute(
                    """INSERT INTO detalle_venta
                       (id_venta, id_producto, cantidad, precio_unitario)
                       VALUES (%s, %s, %s, %s)""",
                    (id_venta, producto.id, cantidad, producto.precio)
                )
            conexion.commit()
            return id_venta
        except (Error, ValueError):
            if conexion and conexion.is_connected():
                conexion.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def importar_venta_legacy(
        self, venta, id_cliente, id_empleado, productos, id_origen
    ):
        if len(productos) != len(venta.get("productos", [])):
            raise ValueError(
                f"La venta {id_origen} tiene productos sin correspondencia."
            )
        fecha = datetime.strptime(venta["fecha"], "%d/%m/%Y %H:%M")
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO ventas
                   (fecha, total, metodo_pago, id_cliente, id_empleado)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    fecha, venta["total"], venta["metodo_pago"],
                    id_cliente, id_empleado
                )
            )
            id_venta = cursor.lastrowid
            for detalle, id_producto in zip(venta["productos"], productos):
                cursor.execute(
                    """INSERT INTO detalle_venta
                       (id_venta, id_producto, cantidad, precio_unitario)
                       VALUES (%s, %s, %s, %s)""",
                    (
                        id_venta, id_producto, detalle["cantidad"],
                        detalle["precio"]
                    )
                )
            cursor.execute(
                """INSERT INTO migracion_json (tipo, id_origen, id_destino)
                   VALUES ('venta', %s, %s)""",
                (str(id_origen), id_venta)
            )
            conexion.commit()
            return id_venta
        except Error:
            if conexion and conexion.is_connected():
                conexion.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
