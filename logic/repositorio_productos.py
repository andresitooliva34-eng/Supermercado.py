import math

from mysql.connector import Error, IntegrityError

from data.conexion import obtener_conexion


class RepositorioProductosMySQL:
    """Acceso a las tablas de productos de las dos versiones del esquema."""

    @staticmethod
    def _resolver_tablas(cursor):
        cursor.execute("SHOW TABLES")
        existentes = {fila[0] for fila in cursor.fetchall()}

        if {"producto", "categoria"}.issubset(existentes):
            producto = "producto"
            categoria = "categoria"
        elif {"productos", "categorias"}.issubset(existentes):
            producto = "productos"
            categoria = "categorias"
        else:
            raise Error(
                "No se encontraron las tablas producto/categoria ni "
                "productos/categorias en la base configurada."
            )

        cursor.execute(f"SHOW COLUMNS FROM {producto}")
        columnas = {fila[0] for fila in cursor.fetchall()}
        return {
            "producto": producto,
            "categoria": categoria,
            "codigo_select": "p.codigo" if "codigo" in columnas else "NULL",
            "codigo_insert": "codigo, " if "codigo" in columnas else "",
            "codigo_values": "%s, " if "codigo" in columnas else "",
            "codigo_update": "codigo = %s, " if "codigo" in columnas else "",
            "codigo_filter": "p.codigo LIKE %s OR " if "codigo" in columnas else "",
            "tiene_codigo": "codigo" in columnas,
        }

    def tiene_codigo(self):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            return self._resolver_tablas(cursor)["tiene_codigo"]
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def _consultar(self, sql, parametros=()):
        conexion = None
        cursor = None

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            tablas = self._resolver_tablas(cursor)
            if callable(parametros):
                parametros = parametros(tablas)
            cursor.execute(sql.format(**tablas), parametros)
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
            tablas = self._resolver_tablas(cursor)
            if callable(sql):
                sql, parametros = sql(tablas)
            cursor.execute(sql.format(**tablas), parametros)
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
            "SELECT id_categoria, nombre FROM {categoria} ORDER BY nombre"
        )

    def listar_productos(self, texto=""):
        patron = f"%{texto}%"
        return self._consultar(
            """SELECT p.id_producto, {codigo_select}, p.nombre,
                      c.nombre, p.precio, p.stock
               FROM {producto} p
               INNER JOIN {categoria} c
                       ON p.id_categoria = c.id_categoria
               WHERE {codigo_filter}p.nombre LIKE %s
                  OR c.nombre LIKE %s
                  OR CAST(p.id_producto AS CHAR) = %s
               ORDER BY p.nombre""",
            lambda tablas: (
                (patron, patron, patron, texto)
                if tablas["tiene_codigo"] else (patron, patron, texto)
            )
        )

    def agregar_producto(self, codigo, nombre, precio, stock, id_categoria):
        self._validar_datos(nombre, precio, stock, id_categoria)
        if codigo is None:
            codigo = ""
        if not isinstance(codigo, str):
            raise ValueError("El código debe ser texto.")
        if codigo and len(codigo.strip()) > 20:
            raise ValueError("El código no puede superar los 20 caracteres.")

        def crear_insert(tablas):
            if tablas["tiene_codigo"] and not codigo.strip():
                raise ValueError("El código es obligatorio.")
            return (
                """INSERT INTO {producto}
                       ({codigo_insert}nombre, precio, stock, id_categoria)
                   VALUES ({codigo_values}%s, %s, %s, %s)""",
                (
                    (codigo.strip(), nombre.strip(), precio, stock, id_categoria)
                    if tablas["tiene_codigo"]
                    else (nombre.strip(), precio, stock, id_categoria)
                )
            )

        try:
            return self._ejecutar_cambio(crear_insert)
        except IntegrityError as error:
            if error.errno == 1452:
                raise ValueError(
                    "La categoría seleccionada no existe en la base de datos."
                ) from error
            if error.errno == 1062 and codigo:
                raise ValueError("Ya existe un producto con ese código.") from error
            raise

    def actualizar_producto(
        self, id_producto, codigo, nombre, precio, stock, id_categoria
    ):
        self._validar_datos(nombre, precio, stock, id_categoria)
        if codigo is None:
            codigo = ""
        if not isinstance(codigo, str):
            raise ValueError("El código debe ser texto.")
        if codigo and len(codigo.strip()) > 20:
            raise ValueError("El código no puede superar los 20 caracteres.")

        def crear_actualizacion(tablas):
            if tablas["tiene_codigo"] and not codigo.strip():
                raise ValueError("El código es obligatorio.")
            return (
                """UPDATE {producto}
                   SET {codigo_update}nombre = %s, precio = %s,
                       stock = %s, id_categoria = %s
                   WHERE id_producto = %s""",
                (
                    (codigo.strip(), nombre.strip(), precio, stock,
                     id_categoria, id_producto)
                    if tablas["tiene_codigo"]
                    else (nombre.strip(), precio, stock, id_categoria,
                          id_producto)
                )
            )

        try:
            self._ejecutar_cambio(crear_actualizacion)
        except IntegrityError as error:
            if error.errno == 1452:
                raise ValueError(
                    "La categoría seleccionada no existe en la base de datos."
                ) from error
            if error.errno == 1062 and codigo:
                raise ValueError("Ya existe otro producto con ese código.") from error
            raise

    def eliminar_producto(self, id_producto):
        try:
            self._ejecutar_cambio(
                "DELETE FROM {producto} WHERE id_producto = %s",
                (id_producto,)
            )
        except IntegrityError as error:
            if error.errno == 1451:
                raise ValueError(
                    "No se puede eliminar el producto porque está asociado "
                    "a una venta."
                ) from error
            raise
