"""Importa los datos JSON existentes a MySQL sin eliminar registros."""

import json
import math
from datetime import datetime
from pathlib import Path

import bcrypt
from mysql.connector import Error

from data.conexion import obtener_conexion


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _hash_clave(clave):
    if clave.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            codificada = clave.encode("ascii")
            bcrypt.checkpw(b"", codificada)
        except (UnicodeEncodeError, ValueError, TypeError) as error:
            raise ValueError(
                "Un empleado tiene un hash bcrypt inválido."
            ) from error
        return clave
    try:
        return bcrypt.hashpw(
            clave.encode("utf-8"), bcrypt.gensalt()
        ).decode("ascii")
    except (UnicodeEncodeError, ValueError) as error:
        raise ValueError(
            "La contraseña de un empleado no se puede convertir a bcrypt "
            "(máximo 72 bytes UTF-8)."
        ) from error


def _leer_json(nombre):
    ruta = DATA_DIR / nombre
    if not ruta.exists():
        raise FileNotFoundError(
            f"Falta el archivo de origen {ruta}. "
            "La migración se canceló sin modificar la base."
        )
    with ruta.open(encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{ruta.name}, línea {error.lineno}: JSON inválido: "
                f"{error.msg}"
            ) from error
    if not isinstance(datos, list):
        raise ValueError(f"{ruta.name} debe contener una lista JSON.")
    return datos


def _validar_registros(nombre, datos, campos):
    ids = set()
    for indice, item in enumerate(datos, start=1):
        etiqueta = f"{nombre}, registro {indice}"
        if not isinstance(item, dict):
            raise ValueError(f"{etiqueta}: se esperaba un objeto JSON.")
        id_origen = item.get("id")
        if (
            not isinstance(id_origen, int)
            or isinstance(id_origen, bool)
            or id_origen < 1
        ):
            raise ValueError(f"{etiqueta}: el id debe ser un entero positivo.")
        if id_origen in ids:
            raise ValueError(f"{etiqueta}: id duplicado {id_origen}.")
        ids.add(id_origen)
        for campo, tipo in campos.items():
            valor = item.get(campo)
            if not isinstance(valor, tipo):
                raise ValueError(
                    f"{etiqueta}: '{campo}' falta o tiene tipo inválido."
                )
    return ids


def _validar_fuentes(fuentes):
    ids = {}
    ids["categorias"] = _validar_registros(
        "categorias.json", fuentes["categorias"],
        {"nombre": str}
    )
    for indice, categoria in enumerate(fuentes["categorias"], start=1):
        if not categoria["nombre"].strip() or len(categoria["nombre"]) > 50:
            raise ValueError(
                f"categorias.json, registro {indice}: nombre inválido."
            )
    nombres_categorias = [
        categoria["nombre"].strip().casefold()
        for categoria in fuentes["categorias"]
    ]
    if len(nombres_categorias) != len(set(nombres_categorias)):
        raise ValueError("categorias.json contiene nombres duplicados.")
    ids["productos"] = _validar_registros(
        "productos.json", fuentes["productos"],
        {"nombre": str, "categoria": str, "precio": (int, float), "stock": int}
    )
    for indice, producto in enumerate(fuentes["productos"], start=1):
        categoria_id = producto.get("categoria_id")
        nombre_categoria = producto["categoria"].strip().casefold()
        categoria_invalida = (
            (
                categoria_id is not None
                and (
                    not isinstance(categoria_id, int)
                    or isinstance(categoria_id, bool)
                    or categoria_id not in ids["categorias"]
                )
            )
            or (
                categoria_id is None
                and nombre_categoria not in nombres_categorias
            )
        )
        if (
            isinstance(producto["precio"], bool)
            or not math.isfinite(producto["precio"])
            or producto["precio"] < 0
            or isinstance(producto["stock"], bool)
            or producto["stock"] < 0
            or not producto["nombre"].strip()
            or len(producto["nombre"]) > 100
            or not producto["categoria"].strip()
            or categoria_invalida
        ):
            raise ValueError(
                f"productos.json, registro {indice}: datos de producto inválidos."
            )

    ids["clientes"] = _validar_registros(
        "clientes.json", fuentes["clientes"],
        {"nombre": str, "apellido": str}
    )
    dnis_clientes = set()
    for indice, cliente in enumerate(fuentes["clientes"], start=1):
        dni_origen = cliente.get("dni")
        telefono = cliente.get("telefono")
        email = cliente.get("email")
        if not all(
            valor is None or isinstance(valor, str)
            for valor in (dni_origen, telefono, email)
        ):
            raise ValueError(
                f"clientes.json, registro {indice}: datos opcionales inválidos."
            )
        dni = (dni_origen or "").replace(".", "").replace(" ", "").strip()
        telefono = telefono or ""
        if dni:
            if dni in dnis_clientes:
                raise ValueError(
                    f"clientes.json, registro {indice}: DNI duplicado."
                )
            dnis_clientes.add(dni)
        if (
            not cliente["nombre"].strip()
            or len(cliente["nombre"]) > 60
            or len(cliente["apellido"]) > 60
            or (dni and (not dni.isdigit() or len(dni) not in (7, 8)))
            or len(telefono) > 20
            or any(
                caracter not in "0123456789 +-()"
                for caracter in telefono
            )
            or (email is not None and len(email) > 100)
        ):
            raise ValueError(
                f"clientes.json, registro {indice}: datos del cliente inválidos."
            )

    ids["empleados"] = _validar_registros(
        "empleados.json", fuentes["empleados"], {}
    )
    empleados_omitidos = []
    usuarios_empleados = set()
    roles_validos = {
        "administrador", "gerente", "supervisor",
        "cajero", "repositor", "vendedor"
    }
    for indice, empleado in enumerate(fuentes["empleados"], start=1):
        faltantes = [
            campo for campo in ("usuario", "clave", "rol")
            if not isinstance(empleado.get(campo), str)
            or not empleado[campo].strip()
        ]
        if faltantes:
            empleados_omitidos.append(
                (indice, empleado["id"], ", ".join(faltantes))
            )
        else:
            usuario = empleado["usuario"].strip().casefold()
            rol = empleado["rol"].strip().casefold()
            nombre_origen = empleado.get("nombre", "Empleado")
            if not isinstance(nombre_origen, str):
                raise ValueError(
                    f"empleados.json, registro {indice}: nombre inválido."
                )
            nombre = nombre_origen.strip().split(maxsplit=1)
            if (
                len(usuario) > 30
                or usuario in usuarios_empleados
                or rol not in roles_validos
                or not nombre
                or len(nombre[0]) > 60
                or (len(nombre) > 1 and len(nombre[1]) > 60)
            ):
                raise ValueError(
                    f"empleados.json, registro {indice}: datos de empleado "
                    "duplicados o fuera de los límites del esquema."
                )
            usuarios_empleados.add(usuario)
            clave = empleado["clave"]
            if clave.startswith(("$2a$", "$2b$", "$2y$")):
                _hash_clave(clave)
            else:
                try:
                    excede_limite_bcrypt = len(clave.encode("utf-8")) > 72
                except UnicodeEncodeError as error:
                    raise ValueError(
                        f"empleados.json, registro {indice}: contraseña inválida."
                    ) from error
                if excede_limite_bcrypt:
                    raise ValueError(
                        f"empleados.json, registro {indice}: contraseña "
                        "mayor a 72 bytes UTF-8; no se importó ningún registro."
                    )

    ids["ventas"] = _validar_registros(
        "ventas.json", fuentes["ventas"],
        {
            "fecha": str, "total": (int, float), "metodo_pago": str,
            "cliente_nombre": str, "productos": list
        }
    )
    for indice, venta in enumerate(fuentes["ventas"], start=1):
        if (
            isinstance(venta["total"], bool)
            or not math.isfinite(venta["total"])
            or venta["total"] < 0
            or not venta["fecha"].strip()
            or not venta["metodo_pago"].strip()
            or not venta["productos"]
        ):
            raise ValueError(
                f"ventas.json, registro {indice}: datos de venta inválidos."
            )
        try:
            datetime.strptime(venta["fecha"], "%d/%m/%Y %H:%M")
        except ValueError as error:
            raise ValueError(
                f"ventas.json, registro {indice}: fecha inválida; "
                "se esperaba DD/MM/AAAA HH:MM."
            ) from error
        for numero, detalle in enumerate(venta["productos"], start=1):
            if not isinstance(detalle, dict):
                raise ValueError(
                    f"ventas.json, registro {indice}, detalle {numero}: "
                    "se esperaba un objeto JSON."
                )
            id_producto = detalle.get("id")
            cantidad = detalle.get("cantidad")
            precio = detalle.get("precio")
            if (
                id_producto not in ids["productos"]
                or not isinstance(cantidad, int)
                or isinstance(cantidad, bool)
                or cantidad <= 0
                or not isinstance(precio, (int, float))
                or isinstance(precio, bool)
                or not math.isfinite(precio)
                or precio < 0
            ):
                raise ValueError(
                    f"ventas.json, registro {indice}, detalle {numero}: "
                    "producto, cantidad o precio inválido."
                )
        cliente_id = venta.get("cliente_id")
        if cliente_id is not None and (
            not isinstance(cliente_id, int)
            or isinstance(cliente_id, bool)
            or cliente_id not in ids["clientes"]
        ):
            raise ValueError(
                f"ventas.json, registro {indice}: cliente_id {cliente_id} "
                "no existe en clientes.json."
            )
        empleado_id = venta.get("empleado_id")
        if empleado_id is not None and (
            not isinstance(empleado_id, int)
            or isinstance(empleado_id, bool)
            or empleado_id not in ids["empleados"]
        ):
            raise ValueError(
                f"ventas.json, registro {indice}: empleado_id "
                f"{empleado_id} no existe en empleados.json."
            )
    return empleados_omitidos


def _ejecutar(sql, parametros=(), fetch=False):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        resultado = cursor.fetchall() if fetch else cursor.lastrowid
        conexion.commit()
        return resultado
    except Error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _crear_tabla_mapeo():
    _ejecutar(
        """CREATE TABLE IF NOT EXISTS migracion_json (
               tipo VARCHAR(20) NOT NULL,
               id_origen VARCHAR(64) NOT NULL,
               id_destino INT NOT NULL,
               PRIMARY KEY (tipo, id_origen)
           ) ENGINE=InnoDB"""
    )


def _destino(tipo, id_origen):
    filas = _ejecutar(
        """SELECT id_destino FROM migracion_json
           WHERE tipo = %s AND id_origen = %s""",
        (tipo, str(id_origen)),
        fetch=True
    )
    return filas[0][0] if filas else None


def _guardar_mapeo(tipo, id_origen, id_destino):
    _ejecutar(
        """INSERT INTO migracion_json (tipo, id_origen, id_destino)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE id_destino = VALUES(id_destino)""",
        (tipo, str(id_origen), id_destino)
    )


def _insertar_mapeado(tipo, id_origen, sql, parametros):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        id_destino = cursor.lastrowid
        cursor.execute(
            """INSERT INTO migracion_json (tipo, id_origen, id_destino)
               VALUES (%s, %s, %s)""",
            (tipo, str(id_origen), id_destino)
        )
        conexion.commit()
        return id_destino
    except Error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _migrar_categorias(datos):
    for item in datos:
        if _destino("categoria", item["id"]) is not None:
            continue
        filas = _ejecutar(
            "SELECT id_categoria FROM categorias WHERE nombre = %s",
            (item["nombre"].strip(),),
            fetch=True
        )
        if filas:
            id_destino = filas[0][0]
            _guardar_mapeo("categoria", item["id"], id_destino)
        else:
            _insertar_mapeado(
                "categoria", item["id"],
                "INSERT INTO categorias (nombre) VALUES (%s)",
                (item["nombre"].strip(),)
            )


def _id_categoria(id_origen):
    id_destino = _destino("categoria", id_origen)
    if id_destino is None:
        raise ValueError(f"No se pudo mapear la categoría JSON {id_origen}.")
    return id_destino


def _migrar_productos(datos):
    for item in datos:
        if _destino("producto", item["id"]) is not None:
            continue
        id_categoria = (
            _id_categoria(item["categoria_id"])
            if "categoria_id" in item else
            _id_categoria_por_nombre(item["categoria"].strip())
        )
        existentes = _ejecutar(
            """SELECT id_producto FROM productos
               WHERE nombre = %s AND precio = %s AND id_categoria = %s
               ORDER BY id_producto LIMIT 1""",
            (item["nombre"], item["precio"], id_categoria),
            fetch=True
        )
        if existentes:
            _guardar_mapeo("producto", item["id"], existentes[0][0])
            continue
        _insertar_mapeado(
            "producto", item["id"],
            """INSERT INTO productos
               (codigo, nombre, precio, stock, id_categoria)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                f"LEG-{item['id']}", item["nombre"], item["precio"],
                item["stock"], id_categoria
            )
        )


def _id_categoria_por_nombre(nombre):
    filas = _ejecutar(
        "SELECT id_categoria FROM categorias WHERE nombre = %s",
        (nombre.strip(),),
        fetch=True
    )
    if not filas:
        raise ValueError(f"No existe la categoría '{nombre}' en MySQL.")
    return filas[0][0]


def _migrar_clientes(datos):
    for item in datos:
        id_destino = _destino("cliente", item["id"])
        if id_destino is not None:
            if item.get("email"):
                _ejecutar(
                    """UPDATE clientes SET email = %s
                       WHERE id_cliente = %s AND (email IS NULL OR email = '')""",
                    (item["email"], id_destino)
                )
            continue
        dni = item.get("dni", "").strip() or None
        filas = (
            _ejecutar(
                "SELECT id_cliente FROM clientes WHERE dni = %s",
                (dni,),
                fetch=True
            )
            if dni else []
        )
        if filas:
            id_destino = filas[0][0]
            _guardar_mapeo("cliente", item["id"], id_destino)
        else:
            _insertar_mapeado(
                "cliente", item["id"],
                """INSERT INTO clientes
                   (nombre, apellido, dni, telefono, email)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    item.get("nombre", "") or "Cliente",
                    item.get("apellido", ""), dni,
                    item.get("telefono") or None, item.get("email") or None
                )
            )


def _migrar_empleados(datos):
    for item in datos:
        if not all(item.get(campo) for campo in ("usuario", "clave", "rol")):
            continue
        if _destino("empleado", item["id"]) is not None:
            continue
        filas = _ejecutar(
            "SELECT id_empleado FROM empleados WHERE usuario = %s",
            (item["usuario"],),
            fetch=True
        )
        hash_clave = _hash_clave(item["clave"])
        partes_nombre = item.get("nombre", "Empleado").split(maxsplit=1)
        nombre = partes_nombre[0]
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
        if filas:
            id_destino = filas[0][0]
            _guardar_mapeo("empleado", item["id"], id_destino)
            continue
        else:
            _insertar_mapeado(
                "empleado", item["id"],
                """INSERT INTO empleados
                   (nombre, apellido, usuario, rol, clave, activo)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    nombre, apellido,
                    item["usuario"], item["rol"].casefold(), hash_clave,
                    int(bool(item.get("activo", True)))
                )
            )
            continue
        _guardar_mapeo("empleado", item["id"], id_destino)


def _migrar_ventas(datos):
    empleados = _leer_json("empleados.json")
    id_admin = next(
        (
            _destino("empleado", item["id"])
            for item in empleados
            if item.get("id") and
            str(item.get("rol", "")).casefold() == "administrador" and
            _destino("empleado", item["id"]) is not None
        ),
        None
    )
    for item in datos:
        if _destino("venta", item["id"]) is not None:
            continue
        id_cliente = _destino("cliente", item.get("cliente_id"))
        id_empleado = _destino("empleado", item.get("empleado_id"))
        if id_empleado is None:
            filas = _ejecutar(
                """SELECT id_empleado FROM empleados
                   WHERE CONCAT_WS(' ', nombre, apellido) = %s""",
                (item.get("empleado_nombre", ""),),
                fetch=True
            )
            id_empleado = filas[0][0] if filas else None
        if id_empleado is None:
            id_empleado = id_admin
        if id_empleado is None:
            raise ValueError(
                f"No se pudo asociar un empleado a la venta {item['id']}; "
                "no hay un administrador JSON migrado para usar como respaldo."
            )
        ids_productos = [
            _destino("producto", detalle["id"])
            for detalle in item.get("productos", [])
        ]
        if any(id_producto is None for id_producto in ids_productos):
            raise ValueError(
                f"No se pudieron asociar los productos de la venta {item['id']}."
            )
        from logic.repositorio_mysql import RepositorioMySQL

        RepositorioMySQL().importar_venta_legacy(
            item, id_cliente, id_empleado, ids_productos, item["id"]
        )


def migrar():
    fuentes = {
        nombre.removesuffix(".json"): _leer_json(nombre)
        for nombre in (
            "categorias.json",
            "productos.json",
            "clientes.json",
            "empleados.json",
            "ventas.json"
        )
    }
    empleados_omitidos = _validar_fuentes(fuentes)

    _crear_tabla_mapeo()
    _migrar_categorias(fuentes["categorias"])
    _migrar_productos(fuentes["productos"])
    _migrar_clientes(fuentes["clientes"])
    _migrar_empleados(fuentes["empleados"])
    _migrar_ventas(fuentes["ventas"])
    return empleados_omitidos


if __name__ == "__main__":
    omitidos = migrar()
    print("Migración JSON a MySQL terminada.")
    if omitidos:
        print("Empleados que requieren completar datos y no se importaron:")
        for indice, id_origen, campos in omitidos:
            print(
                f"  empleados.json registro {indice} "
                f"(id={id_origen}): faltan {campos}."
            )
