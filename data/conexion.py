import json
import os
from pathlib import Path
 
import mysql.connector
from mysql.connector import Error
 
 
# Ruta del archivo con la configuración de la base de datos.
# Cada integrante tiene el suyo (NO se sube a GitHub).
RUTA_CONFIG = Path(__file__).resolve().parent / "config_db.json"
 
 
def cargar_configuracion(administrativa=False):
    """Carga la configuración local y permite sobreescribirla por entorno."""
    if RUTA_CONFIG.exists():
        with open(RUTA_CONFIG, encoding="utf-8") as archivo:
            configuracion = json.load(archivo)
    else:
        configuracion = {}
    if not isinstance(configuracion, dict):
        raise ValueError("La configuración de MySQL debe ser un objeto JSON.")

    variables_entorno = {
        "host": "SUPERMERCADO_DB_HOST",
        "port": "SUPERMERCADO_DB_PORT",
        "user": "SUPERMERCADO_DB_USER",
        "password": "SUPERMERCADO_DB_PASSWORD",
        "database": "SUPERMERCADO_DB_NAME",
        "admin_user": "SUPERMERCADO_DB_ADMIN_USER",
        "admin_password": "SUPERMERCADO_DB_ADMIN_PASSWORD"
    }
    for clave, variable in variables_entorno.items():
        valor = os.getenv(variable)
        if valor:
            configuracion[clave] = valor

    obligatorias = ("host", "user", "password", "database")
    faltantes = [clave for clave in obligatorias if not configuracion.get(clave)]
    if faltantes:
        raise FileNotFoundError(
            "Falta configurar MySQL. Completá data/config_db.json "
            "a partir de data/config_db.example.json o definí las variables "
            "SUPERMERCADO_DB_HOST, SUPERMERCADO_DB_USER, "
            "SUPERMERCADO_DB_PASSWORD y SUPERMERCADO_DB_NAME. "
            f"Campos faltantes: {', '.join(faltantes)}."
        )
    if configuracion["password"] == "CONFIGURAR_LOCALMENTE":
        raise ValueError(
            "Reemplazá CONFIGURAR_LOCALMENTE por la contraseña de cm_cajero "
            "en data/config_db.json."
        )
    for clave in ("host", "user", "password", "database"):
        if not isinstance(configuracion[clave], str):
            raise ValueError(f"El campo '{clave}' de MySQL debe ser texto.")
    for clave in ("admin_user", "admin_password"):
        if clave in configuracion and not isinstance(configuracion[clave], str):
            raise ValueError(f"El campo '{clave}' de MySQL debe ser texto.")
    for clave in ("host", "user", "database"):
        if not configuracion[clave].strip():
            raise ValueError(f"El campo '{clave}' de MySQL no puede estar vacío.")

    puerto = configuracion.get("port", 3306)
    if isinstance(puerto, bool) or not isinstance(puerto, (int, str)):
        raise ValueError("El puerto de MySQL debe ser un número entero.")
    try:
        configuracion["port"] = int(puerto)
    except (TypeError, ValueError) as error:
        raise ValueError("El puerto de MySQL debe ser un número entero.") from error
    if not 1 <= configuracion["port"] <= 65535:
        raise ValueError("El puerto de MySQL debe estar entre 1 y 65535.")

    if configuracion["user"] != "cm_cajero":
        raise ValueError(
            "La conexión operativa debe usar cm_cajero. Configurá también "
            "admin_user y admin_password para las funciones administrativas."
        )

    if administrativa:
        faltantes_admin = [
            clave for clave in ("admin_user", "admin_password")
            if not configuracion.get(clave)
        ]
        if faltantes_admin:
            raise FileNotFoundError(
                "Faltan las credenciales de administración en "
                "data/config_db.json: "
                f"{', '.join(faltantes_admin)}."
            )
        if configuracion["admin_user"] != "cm_admin":
            raise ValueError("La conexión administrativa debe usar cm_admin.")
        if configuracion["admin_password"] == "CONFIGURAR_LOCALMENTE":
            raise ValueError(
                "Reemplazá CONFIGURAR_LOCALMENTE por la contraseña de "
                "cm_admin en data/config_db.json."
            )
        configuracion["user"] = configuracion["admin_user"]
        configuracion["password"] = configuracion["admin_password"]
    return configuracion


def obtener_conexion(administrativa=False):
    """Crea y devuelve una conexión nueva a la base codemarket."""
    config = cargar_configuracion(administrativa=administrativa)
 
    return mysql.connector.connect(
        host=config["host"],
        port=config["port"],
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
 
        cursor.execute("SELECT COUNT(*) FROM productos")
        cantidad = cursor.fetchone()[0]
 
        print(f"Conexión exitosa. Productos en la base: {cantidad}")
 
    except (Error, FileNotFoundError, ValueError) as error:
        print("No se pudo conectar:", error)
 
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()
 
 
if __name__ == "__main__":
    probar_conexion()
