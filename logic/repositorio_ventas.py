from datetime import datetime

from data.conexion import obtener_conexion
from logic.repositorio_base_mysql import RepositorioMySQLBase
from mysql.connector import Error


class RepositorioVentasMySQL(RepositorioMySQLBase):
    """Consulta, registro y migración de ventas."""

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
            conexion = obtener_conexion(administrativa=True)
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
        except (Error, ValueError):
            if conexion and conexion.is_connected():
                conexion.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
