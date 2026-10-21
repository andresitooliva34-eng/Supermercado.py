"""Importa los datos JSON existentes a MySQL sin eliminar registros."""

import json
from pathlib import Path

import bcrypt
from mysql.connector import Error

from data.conexion import obtener_conexion


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _leer_json(nombre):
    ruta = DATA_DIR / nombre
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, list):
        raise ValueError(f"{ruta.name} debe contener una lista JSON.")
    return datos


def _ejecutar(sql, parametros=(), fetch=False):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        resultado = cursor.fetchall() if fetch else cursor.lastrowid
        conexion.commit()
        return resultado
    except Error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _crear_tabla_mapeo():
    _ejecutar(
        """CREATE TABLE IF NOT EXISTS migracion_json (
               tipo VARCHAR(20) NOT NULL,
               id_origen VARCHAR(64) NOT NULL,
               id_destino INT NOT NULL,
               PRIMARY KEY (tipo, id_origen)
           ) ENGINE=InnoDB"""
    )


def _destino(tipo, id_origen):
    filas = _ejecutar(
        """SELECT id_destino FROM migracion_json
           WHERE tipo = %s AND id_origen = %s""",
        (tipo, str(id_origen)),
        fetch=True
    )
    return filas[0][0] if filas else None


def _guardar_mapeo(tipo, id_origen, id_destino):
    _ejecutar(
        """INSERT INTO migracion_json (tipo, id_origen, id_destino)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE id_destino = VALUES(id_destino)""",
        (tipo, str(id_origen), id_destino)
    )


def _insertar_mapeado(tipo, id_origen, sql, parametros):
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        id_destino = cursor.lastrowid
        cursor.execute(
            """INSERT INTO migracion_json (tipo, id_origen, id_destino)
               VALUES (%s, %s, %s)""",
            (tipo, str(id_origen), id_destino)
        )
        conexion.commit()
        return id_destino
    except Error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def _migrar_categorias(datos):
    for item in datos:
        if _destino("categoria", item["id"]) is not None:
            continue
        filas = _ejecutar(
            "SELECT id_categoria FROM categorias WHERE nombre = %s",
            (item["nombre"],),
            fetch=True
        )
        if filas:
            id_destino = filas[0][0]
            _guardar_mapeo("categoria", item["id"], id_destino)
        else:
            _insertar_mapeado(
                "categoria", item["id"],
                "INSERT INTO categorias (nombre) VALUES (%s)",
                (item["nombre"],)
            )


def _id_categoria(id_origen):
    id_destino = _destino("categoria", id_origen)
    if id_destino is None:
        raise ValueError(f"No se pudo mapear la categoría JSON {id_origen}.")
    return id_destino


def _migrar_productos(datos):
    for item in datos:
        if _destino("producto", item["id"]) is not None:
            continue
        id_categoria = (
            _id_categoria(item["categoria_id"])
            if "categoria_id" in item else
            _id_categoria_por_nombre(item["categoria"])
        )
        existentes = _ejecutar(
            """SELECT id_producto FROM productos
               WHERE nombre = %s AND precio = %s AND id_categoria = %s
               ORDER BY id_producto LIMIT 1""",
            (item["nombre"], item["precio"], id_categoria),
            fetch=True
        )
        if existentes:
            _guardar_mapeo("producto", item["id"], existentes[0][0])
            continue
        _insertar_mapeado(
            "producto", item["id"],
            """INSERT INTO productos
               (codigo, nombre, precio, stock, id_categoria)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                f"LEG-{item['id']}", item["nombre"], item["precio"],
                item["stock"], id_categoria
            )
        )


def _id_categoria_por_nombre(nombre):
    filas = _ejecutar(
        "SELECT id_categoria FROM categorias WHERE nombre = %s",
        (nombre,),
        fetch=True
    )
    if not filas:
        raise ValueError(f"No existe la categoría '{nombre}' en MySQL.")
    return filas[0][0]


def _migrar_clientes(datos):
    for item in datos:
        id_destino = _destino("cliente", item["id"])
        if id_destino is not None:
            if item.get("email"):
                _ejecutar(
                    """UPDATE clientes SET email = %s
                       WHERE id_cliente = %s AND (email IS NULL OR email = '')""",
                    (item["email"], id_destino)
                )
            continue
        dni = item.get("dni", "").strip() or None
        filas = (
            _ejecutar(
                "SELECT id_cliente FROM clientes WHERE dni = %s",
                (dni,),
                fetch=True
            )
            if dni else []
        )
        if filas:
            id_destino = filas[0][0]
            _ejecutar(
                """UPDATE clientes
                   SET nombre = %s, apellido = %s, telefono = %s, email = %s
                   WHERE id_cliente = %s""",
                (
                    item.get("nombre", "") or "Cliente",
                    item.get("apellido", ""),
                    item.get("telefono") or None,
                    item.get("email") or None,
                    id_destino
                )
            )
            _guardar_mapeo("cliente", item["id"], id_destino)
        else:
            _insertar_mapeado(
                "cliente", item["id"],
                """INSERT INTO clientes
                   (nombre, apellido, dni, telefono, email)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    item.get("nombre", "") or "Cliente",
                    item.get("apellido", ""), dni,
                    item.get("telefono") or None, item.get("email") or None
                )
            )


def _migrar_empleados(datos):
    for item in datos:
        if not all(item.get(campo) for campo in ("usuario", "clave", "rol")):
            print(
                f"Se omite el empleado JSON id={item.get('id')}: "
                "faltan usuario, clave o rol."
            )
            continue
        if _destino("empleado", item["id"]) is not None:
            continue
        filas = _ejecutar(
            "SELECT id_empleado FROM empleados WHERE usuario = %s",
            (item["usuario"],),
            fetch=True
        )
        hash_clave = bcrypt.hashpw(
            item["clave"].encode("utf-8"), bcrypt.gensalt()
        ).decode("ascii")
        partes_nombre = item.get("nombre", "Empleado").split(maxsplit=1)
        nombre = partes_nombre[0]
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
        if filas:
            id_destino = filas[0][0]
            _ejecutar(
                """UPDATE empleados
                   SET nombre = %s, apellido = %s, rol = %s,
                       clave = %s, activo = %s
                   WHERE id_empleado = %s""",
                (
                    nombre, apellido,
                    item["rol"].casefold(),
                    hash_clave, int(bool(item.get("activo", True))), id_destino
                )
            )
        else:
            _insertar_mapeado(
                "empleado", item["id"],
                """INSERT INTO empleados
                   (nombre, apellido, usuario, rol, clave, activo)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    nombre, apellido,
                    item["usuario"], item["rol"].casefold(), hash_clave,
                    int(bool(item.get("activo", True)))
                )
            )
            continue
        _guardar_mapeo("empleado", item["id"], id_destino)


def _migrar_ventas(datos):
    empleados = _leer_json("empleados.json")
    id_admin = next(
        (
            _destino("empleado", item["id"])
            for item in empleados
            if item.get("id") and
            str(item.get("rol", "")).casefold() == "administrador" and
            _destino("empleado", item["id"]) is not None
        ),
        None
    )
    for item in datos:
        if _destino("venta", item["id"]) is not None:
            continue
        id_cliente = _destino("cliente", item.get("cliente_id"))
        id_empleado = _destino("empleado", item.get("empleado_id"))
        if id_empleado is None:
            filas = _ejecutar(
                """SELECT id_empleado FROM empleados
                   WHERE CONCAT_WS(' ', nombre, apellido) = %s""",
                (item.get("empleado_nombre", ""),),
                fetch=True
            )
            id_empleado = filas[0][0] if filas else None
        if id_empleado is None:
            id_empleado = id_admin
        if id_empleado is None:
            raise ValueError(
                f"No se pudo asociar un empleado a la venta {item['id']}; "
                "no hay un administrador JSON migrado para usar como respaldo."
            )
        ids_productos = [
            _destino("producto", detalle["id"])
            for detalle in item.get("productos", [])
        ]
        if any(id_producto is None for id_producto in ids_productos):
            raise ValueError(
                f"No se pudieron asociar los productos de la venta {item['id']}."
            )
        from logic.repositorio_mysql import RepositorioMySQL

        RepositorioMySQL().importar_venta_legacy(
            item, id_cliente, id_empleado, ids_productos, item["id"]
        )


def migrar():
    _crear_tabla_mapeo()
    _migrar_categorias(_leer_json("categorias.json"))
    _migrar_productos(_leer_json("productos.json"))
    _migrar_clientes(_leer_json("clientes.json"))
    _migrar_empleados(_leer_json("empleados.json"))
    _migrar_ventas(_leer_json("ventas.json"))


if __name__ == "__main__":
    migrar()
    print("Migración JSON a MySQL terminada.")
