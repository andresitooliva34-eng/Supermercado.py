from mysql.connector import IntegrityError

from logic.cliente import Cliente
from logic.repositorio_base_mysql import RepositorioMySQLBase
from logic.validaciones import dni_valido, limpiar_dni, telefono_valido


class RepositorioClientesMySQL(RepositorioMySQLBase):
    """Persistencia de clientes."""

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
            (id_cliente,),
            administrativa=True
        )

    def guardar_cliente_registro(self, registro):
        cliente = Cliente(
            registro.get("id", 0),
            registro["nombre"],
            registro.get("apellido", ""),
            registro.get("dni", ""),
            registro.get("telefono", "")
        )
        registro["id"] = self.guardar_cliente(cliente)
        return registro["id"]
