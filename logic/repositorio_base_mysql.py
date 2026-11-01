from mysql.connector import Error

from data.conexion import obtener_conexion


class RepositorioMySQLBase:
    """Operaciones comunes de conexión para los repositorios MySQL."""

    def _consultar(self, sql, parametros=(), administrativa=False):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion(administrativa=administrativa)
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def _ejecutar(self, sql, parametros=(), administrativa=False):
        conexion = None
        cursor = None
        try:
            conexion = obtener_conexion(administrativa=administrativa)
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
