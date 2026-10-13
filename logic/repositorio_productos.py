from mysql.connector import Error, IntegrityError

from data.conexion import obtener_conexion


class RepositorioProductosMySQL:
    """
    Se encarga de hablar con las tablas producto y categoria de MySQL.
    Acá está TODO el SQL de productos; la interfaz no escribe SQL.
    """

    def _consultar(self, sql, parametros=()):
        # Ejecuta un SELECT y devuelve todas las filas encontradas
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


    def listar_categorias(self):
        # Devuelve [(id_categoria, nombre), ...] para llenar el Combobox
        return self._consultar(
            "SELECT id_categoria, nombre "
            "FROM categoria "
            "ORDER BY nombre"
        )


    def listar_productos(self, texto=""):
        # CONSULTA: busca por nombre (parcial) o por ID (exacto).
        # Si texto está vacío, el LIKE '%%' devuelve todos los productos.
        patron = f"%{texto}%"

        return self._consultar(
            """SELECT p.id_producto, p.nombre, c.nombre, p.precio, p.stock
               FROM producto p
               INNER JOIN categoria c
                       ON p.id_categoria = c.id_categoria
               WHERE p.nombre LIKE %s OR CAST(p.id_producto AS CHAR) = %s
               ORDER BY p.nombre""",
            (patron, texto)
        )


    def agregar_producto(self, nombre, precio, stock, id_categoria):
        # ALTA: valida los datos y hace el INSERT. Devuelve el id nuevo.
        if not nombre.strip():
            raise ValueError("El nombre es obligatorio.")

        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")

        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        conexion = None
        cursor = None

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(
                """INSERT INTO producto (nombre, precio, stock, id_categoria)
                   VALUES (%s, %s, %s, %s)""",
                (nombre.strip(), precio, stock, id_categoria)
            )

            conexion.commit()
            return cursor.lastrowid

        except IntegrityError:
            # Se rompió una regla de la base (por ejemplo, categoría inexistente)
            raise ValueError("La base rechazó el dato: revisá la categoría elegida.")

        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()
