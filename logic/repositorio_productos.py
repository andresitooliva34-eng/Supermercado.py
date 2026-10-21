import math

from mysql.connector import Error, IntegrityError

from data.conexion import obtener_conexion


class RepositorioProductosMySQL:
    """CRUD del catálogo de la base codemarket existente."""

    @staticmethod
    def _conectar():
        return obtener_conexion()

    def listar_categorias(self):
        conexion = None
        cursor = None
        try:
            conexion = self._conectar()
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT id_categoria, nombre FROM categorias ORDER BY nombre"
            )
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def listar_productos(self, texto=""):
        conexion = None
        cursor = None
        patron = f"%{texto}%"
        try:
            conexion = self._conectar()
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT p.id_producto, p.codigo, p.nombre, c.nombre,
                          p.precio, p.stock
                   FROM productos p
                   JOIN categorias c ON c.id_categoria = p.id_categoria
                   WHERE p.nombre LIKE %s OR c.nombre LIKE %s
                      OR p.codigo LIKE %s
                      OR CAST(p.id_producto AS CHAR) = %s
                   ORDER BY p.nombre""",
                (patron, patron, patron, texto)
            )
            return cursor.fetchall()
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

    @staticmethod
    def _validar_codigo(codigo):
        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código es obligatorio.")
        if len(codigo.strip()) > 20:
            raise ValueError("El código no puede superar los 20 caracteres.")

    def agregar_producto(self, codigo, nombre, precio, stock, id_categoria):
        self._validar_datos(nombre, precio, stock, id_categoria)
        self._validar_codigo(codigo)
        conexion = None
        cursor = None
        try:
            conexion = self._conectar()
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO productos
                   (codigo, nombre, precio, stock, id_categoria)
                   VALUES (%s, %s, %s, %s, %s)""",
                (codigo.strip(), nombre.strip(), precio, stock, id_categoria)
            )
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

    def actualizar_producto(
        self, id_producto, codigo, nombre, precio, stock, id_categoria
    ):
        self._validar_datos(nombre, precio, stock, id_categoria)
        self._validar_codigo(codigo)
        self._cambiar(
            """UPDATE productos
               SET codigo = %s, nombre = %s, precio = %s, stock = %s,
                   id_categoria = %s
               WHERE id_producto = %s""",
            (codigo.strip(), nombre.strip(), precio, stock, id_categoria,
             id_producto)
        )

    def eliminar_producto(self, id_producto):
        try:
            self._cambiar(
                "DELETE FROM productos WHERE id_producto = %s",
                (id_producto,)
            )
        except IntegrityError as error:
            if error.errno == 1451:
                raise ValueError(
                    "No se puede eliminar el producto porque está asociado "
                    "a una venta."
                ) from error
            raise

    def _cambiar(self, sql, parametros):
        conexion = None
        cursor = None
        try:
            conexion = self._conectar()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)
            conexion.commit()
        except Error:
            if conexion and conexion.is_connected():
                conexion.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
