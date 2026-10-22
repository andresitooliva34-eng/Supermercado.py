"""Crea la primera cuenta administradora con una contraseña bcrypt."""

import getpass
import sys

from mysql.connector import Error

from data.conexion import obtener_conexion
from logic.repositorio_mysql import RepositorioMySQL


def crear_administrador():
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """SELECT COUNT(*) FROM empleados
               WHERE LOWER(rol) IN ('administrador', 'gerente')
                 AND activo = 1"""
        )
        if cursor.fetchone()[0]:
            raise ValueError(
                "Ya existe una cuenta activa de Administrador o Gerente. "
                "Gestioná las cuentas desde Administración → Empleados."
            )
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

    nombre = input("Nombre y apellido del administrador: ").strip()
    usuario = input("Usuario nuevo: ").strip()
    clave = getpass.getpass("Contraseña (mínimo 12 caracteres): ")
    confirmacion = getpass.getpass("Repetí la contraseña: ")
    if not nombre or not usuario:
        raise ValueError("El nombre y el usuario son obligatorios.")
    if len(clave) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres.")
    if clave != confirmacion:
        raise ValueError("Las contraseñas no coinciden.")

    empleado = {
        "nombre": nombre,
        "usuario": usuario,
        "rol": "Administrador",
        "activo": True
    }
    RepositorioMySQL().guardar_empleado(empleado, clave)
    print("Cuenta de Administrador creada. La contraseña no se muestra.")


if __name__ == "__main__":
    try:
        crear_administrador()
    except (Error, FileNotFoundError, ValueError) as error:
        print(f"No se pudo crear la cuenta: {error}", file=sys.stderr)
        raise SystemExit(1) from error
