import json
from pathlib import Path
 
import mysql.connector
from mysql.connector import Error
 
 
# Ruta del archivo con la configuración de la base de datos.
# Cada integrante tiene el suyo (NO se sube a GitHub).
RUTA_CONFIG = Path(__file__).resolve().parent / "config_db.json"
 
 
def cargar_configuracion():
    """Lee host, usuario, contraseña y base desde config_db.json."""
    if not RUTA_CONFIG.exists():
        raise FileNotFoundError(
            "Falta data/config_db.json. "
            "Copiá data/config_db.example.json con ese nombre "
            "y completá tus datos."
        )
 
    with open(RUTA_CONFIG, encoding="utf-8") as archivo:
        return json.load(archivo)
 
 
def obtener_conexion():
    """Crea y devuelve una conexión nueva a la base codemarket."""
    config = cargar_configuracion()
 
    return mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
 
 
def probar_conexion():
    """Prueba la conexión y muestra cuántos productos hay."""
    conexion = None
    cursor = None
 
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
 
        cursor.execute("SELECT COUNT(*) FROM producto")
        cantidad = cursor.fetchone()[0]
 
        print(f"Conexión exitosa. Productos en la base: {cantidad}")
 
    except (Error, FileNotFoundError) as error:
        print("No se pudo conectar:", error)
 
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
 
 
if __name__ == "__main__":
    probar_conexion()