import bcrypt
from mysql.connector import IntegrityError

from logic.repositorio_base_mysql import RepositorioMySQLBase


def _normalizar_rol(rol):
    roles = {
        "administrador": "Administrador",
        "gerente": "Gerente",
        "supervisor": "Supervisor",
        "cajero": "Cajero",
        "repositor": "Repositor",
        "vendedor": "Vendedor"
    }
    return roles.get(str(rol).casefold(), str(rol))


class RepositorioEmpleadosMySQL(RepositorioMySQLBase):
    """Persistencia y autenticación de empleados."""

    def listar_empleados(self):
        return [
            {
                "id": fila[0],
                "nombre": f"{fila[1]} {fila[2]}".strip(),
                "dni": "",
                "rol": _normalizar_rol(fila[4]),
                "usuario": fila[3],
                "activo": bool(fila[5])
            }
            for fila in self._consultar(
                """SELECT id_empleado, nombre, apellido, usuario, rol, activo
                   FROM empleados ORDER BY nombre, apellido"""
            )
        ]

    def autenticar_empleado(self, usuario, clave):
        filas = self._consultar(
            """SELECT id_empleado, nombre, apellido, usuario, rol, clave, activo
               FROM empleados WHERE usuario = %s""",
            (usuario,)
        )
        if not filas:
            return None
        fila = filas[0]
        hash_clave = fila[5]
        if not isinstance(hash_clave, str) or not hash_clave:
            return None
        try:
            valida = bcrypt.checkpw(
                clave.encode("utf-8"),
                hash_clave.encode("ascii")
            )
        except (ValueError, TypeError):
            valida = False
        if not valida and not hash_clave.startswith(("$2a$", "$2b$", "$2y$")):
            valida = hash_clave == clave
            if valida:
                nuevo_hash = bcrypt.hashpw(
                    clave.encode("utf-8"), bcrypt.gensalt()
                ).decode("ascii")
                self._ejecutar(
                    "UPDATE empleados SET clave = %s WHERE id_empleado = %s",
                    (nuevo_hash, fila[0]),
                    administrativa=True
                )
        if not valida or not fila[6]:
            return None
        return {
            "id": fila[0],
            "nombre": f"{fila[1]} {fila[2]}".strip(),
            "dni": "",
            "rol": _normalizar_rol(fila[4]),
            "usuario": fila[3],
            "activo": bool(fila[6])
        }

    def guardar_empleado(self, empleado, clave=None):
        nombre_completo = empleado.get("nombre")
        usuario = empleado.get("usuario")
        rol = empleado.get("rol")
        if not all(isinstance(valor, str) for valor in (nombre_completo, usuario, rol)):
            raise ValueError("Nombre, usuario y rol deben ser texto.")
        partes_nombre = nombre_completo.strip().split(maxsplit=1)
        nombre = partes_nombre[0] if partes_nombre else ""
        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
        usuario = usuario.strip()
        rol = rol.strip()
        if not nombre or len(nombre) > 60:
            raise ValueError("El nombre es obligatorio y admite hasta 60 caracteres.")
        if len(apellido) > 60:
            raise ValueError("El apellido admite hasta 60 caracteres.")
        if not usuario or len(usuario) > 30:
            raise ValueError("El usuario es obligatorio y admite hasta 30 caracteres.")
        if not rol or len(rol) > 20:
            raise ValueError("El rol es obligatorio y admite hasta 20 caracteres.")
        if not empleado.get("id") and clave is None:
            raise ValueError("La contraseña es obligatoria para un empleado nuevo.")
        if clave is not None and (
            not isinstance(clave, str)
            or len(clave) < 12
            or len(clave.encode("utf-8")) > 72
        ):
            raise ValueError(
                "La contraseña debe tener al menos 12 caracteres "
                "y no superar 72 bytes UTF-8."
            )
        parametros = (
            nombre, apellido, usuario, rol.casefold(),
            int(bool(empleado.get("activo", True)))
        )
        try:
            if empleado.get("id"):
                if clave:
                    hash_clave = bcrypt.hashpw(
                        clave.encode("utf-8"), bcrypt.gensalt()
                    ).decode("ascii")
                    self._ejecutar(
                        """UPDATE empleados
                           SET nombre = %s, apellido = %s, usuario = %s, rol = %s,
                               activo = %s, clave = %s
                           WHERE id_empleado = %s""",
                        (*parametros, hash_clave, empleado["id"]),
                        administrativa=True
                    )
                else:
                    self._ejecutar(
                        """UPDATE empleados
                           SET nombre = %s, apellido = %s, usuario = %s, rol = %s,
                               activo = %s
                           WHERE id_empleado = %s""",
                        (*parametros, empleado["id"]),
                        administrativa=True
                    )
                return empleado["id"]
            hash_clave = bcrypt.hashpw(
                clave.encode("utf-8"), bcrypt.gensalt()
            ).decode("ascii")
            return self._ejecutar(
                """INSERT INTO empleados
                   (nombre, apellido, usuario, rol, clave, activo)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    parametros[0], parametros[1], parametros[2], parametros[3],
                    hash_clave, parametros[4]
                ),
                administrativa=True
            )
        except IntegrityError as error:
            if error.errno == 1062:
                raise ValueError("Ese usuario ya está registrado.") from error
            raise

    def eliminar_empleado(self, id_empleado):
        self._ejecutar(
            "DELETE FROM empleados WHERE id_empleado = %s",
            (id_empleado,),
            administrativa=True
        )
