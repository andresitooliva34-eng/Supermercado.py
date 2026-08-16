import mysql.connector
from mysql.connector import Error
import json
from pathlib import Path


def obtener_conexion():
    """Crea y devuelve una conexión con la base de datos supermercado."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nany2090#",
        database="supermercado"
    )


def obtener_productos():
    """Obtiene los productos para que puedan usarse desde la aplicación."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre, categoria, precio, stock FROM productos")
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def sincronizar_productos_desde_json():
    """Crea la tabla e importa los productos iniciales, sin duplicarlos."""
    ruta_json = Path(__file__).resolve().parent / "productos.json"
    with open(ruta_json, encoding="utf-8") as archivo:
        productos = json.load(archivo)

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INT PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                categoria VARCHAR(80) NOT NULL,
                precio DECIMAL(10, 2) NOT NULL,
                stock INT NOT NULL
            )
        """)
        cursor.executemany(
            """INSERT IGNORE INTO productos (id, nombre, categoria, precio, stock)
               VALUES (%(id)s, %(nombre)s, %(categoria)s, %(precio)s, %(stock)s)""",
            productos
        )
        conexion.commit()
        return cursor.rowcount
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def actualizar_productos(productos):
    """Actualiza en MySQL el stock y datos de los objetos Producto recibidos."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.executemany(
            """UPDATE productos
               SET nombre = %s, categoria = %s, precio = %s, stock = %s
               WHERE id = %s""",
            [(p.nombre, p.categoria, p.precio, p.stock, p.id) for p in productos]
        )
        conexion.commit()
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def probar_conexion():
    """Muestra por consola la cantidad y hasta cinco productos de MySQL."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM productos")
        print("Total productos:", cursor.fetchone()[0])

        cursor.execute("SELECT * FROM productos LIMIT 5")
        for fila in cursor.fetchall():
            print(fila)

        print("Conexión exitosa.")
    except Error as error:
        print("Error de conexión con MySQL:", error)
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


if __name__ == "__main__":
    try:
        agregados = sincronizar_productos_desde_json()
        print(f"Productos nuevos importados: {agregados}")
        probar_conexion()
    except Error as error:
        print("Error de conexión con MySQL:", error)
