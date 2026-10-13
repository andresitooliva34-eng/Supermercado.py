import math

from mysql.connector import Error, IntegrityError

from data.conexion import obtener_conexion


class RepositorioProductosMySQL:
    """Acceso a las tablas producto y categoria de MySQL."""

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

    def _ejecutar_cambio(self, sql, parametros=()):
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

    @staticmethod
    def _validar_datos(nombre, precio, stock, id_categoria):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")

        if len(nombre.strip()) > 100:
            raise ValueError("El nombre no puede superar los 100 caracteres.")

        if not isinstance(precio, (int, float)) or not math.isfinite(precio):
            raise ValueError("El precio debe ser un número válido.")

        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")

        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            raise ValueError("El stock debe ser un entero mayor o igual a cero.")

        if not isinstance(id_categoria, int) or id_categoria < 1:
            raise ValueError("Elegí una categoría válida.")

    def listar_categorias(self):
        return self._consultar(
            "SELECT id_categoria, nombre FROM categoria ORDER BY nombre"
        )

    def listar_productos(self, texto=""):
        patron = f"%{texto}%"
        return self._consultar(
            """SELECT p.id_producto, p.nombre, c.nombre, p.precio, p.stock
               FROM producto p
               INNER JOIN categoria c
                       ON p.id_categoria = c.id_categoria
               WHERE p.nombre LIKE %s
                  OR c.nombre LIKE %s
                  OR CAST(p.id_producto AS CHAR) = %s
               ORDER BY p.nombre""",
            (patron, patron, texto)
        )

    def agregar_producto(self, nombre, precio, stock, id_categoria):
        self._validar_datos(nombre, precio, stock, id_categoria)
        try:
            return self._ejecutar_cambio(
                """INSERT INTO producto (nombre, precio, stock, id_categoria)
                   VALUES (%s, %s, %s, %s)""",
                (nombre.strip(), precio, stock, id_categoria)
            )
        except IntegrityError as error:
            if error.errno == 1452:
                raise ValueError(
                    "La categoría seleccionada no existe en la base de datos."
                ) from error
            raise

    def actualizar_producto(
        self, id_producto, nombre, precio, stock, id_categoria
    ):
        self._validar_datos(nombre, precio, stock, id_categoria)
        try:
            self._ejecutar_cambio(
                """UPDATE producto
                   SET nombre = %s, precio = %s, stock = %s, id_categoria = %s
                   WHERE id_producto = %s""",
                (nombre.strip(), precio, stock, id_categoria, id_producto)
            )
        except IntegrityError as error:
            if error.errno == 1452:
                raise ValueError(
                    "La categoría seleccionada no existe en la base de datos."
                ) from error
            raise

    def eliminar_producto(self, id_producto):
        try:
            self._ejecutar_cambio(
                "DELETE FROM producto WHERE id_producto = %s",
                (id_producto,)
            )
        except IntegrityError as error:
            if error.errno == 1451:
                raise ValueError(
                    "No se puede eliminar el producto porque está asociado "
                    "a una venta."
                ) from error
            raise
