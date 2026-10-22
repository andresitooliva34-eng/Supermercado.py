import bcrypt
import unittest
from unittest.mock import patch

from mysql.connector import IntegrityError

from logic.cliente import Cliente
from logic.migrar_json_mysql import _hash_clave, _validar_fuentes
from logic.repositorio_mysql import RepositorioMySQL


def fuentes_validas():
    return {
        "categorias": [{"id": 1, "nombre": "Alimentos"}],
        "productos": [{
            "id": 1,
            "nombre": "Arroz",
            "categoria": "Alimentos",
            "precio": 100,
            "stock": 5
        }],
        "clientes": [{
            "id": 1,
            "nombre": "Ana",
            "apellido": "López",
            "dni": "",
            "telefono": ""
        }],
        "empleados": [{
            "id": 1,
            "usuario": "ana",
            "clave": "clave-legada",
            "rol": "administrador"
        }],
        "ventas": [{
            "id": 1,
            "fecha": "01/05/2025 12:30",
            "total": 100,
            "metodo_pago": "Efectivo",
            "cliente_nombre": "Ana López",
            "cliente_id": 1,
            "productos": [{"id": 1, "cantidad": 1, "precio": 100}]
        }]
    }


class MigracionJsonTests(unittest.TestCase):
    def test_hash_de_contrasena_textual_se_convierte_a_bcrypt(self):
        hashed = _hash_clave("clave-legada")

        self.assertTrue(hashed.startswith("$2"))
        self.assertTrue(bcrypt.checkpw(b"clave-legada", hashed.encode("ascii")))

    def test_hash_bcrypt_existente_se_conserva(self):
        hashed = bcrypt.hashpw(b"clave-legada", bcrypt.gensalt(rounds=4)).decode()

        self.assertEqual(_hash_clave(hashed), hashed)

    def test_rechaza_categoria_inexistente_antes_de_importar(self):
        fuentes = fuentes_validas()
        fuentes["productos"][0]["categoria_id"] = 99

        with self.assertRaisesRegex(ValueError, "datos de producto inválidos"):
            _validar_fuentes(fuentes)

    def test_rechaza_fecha_de_venta_invalida(self):
        fuentes = fuentes_validas()
        fuentes["ventas"][0]["fecha"] = "ayer"

        with self.assertRaisesRegex(ValueError, "fecha inválida"):
            _validar_fuentes(fuentes)

    def test_rechaza_empleado_de_venta_inexistente(self):
        fuentes = fuentes_validas()
        fuentes["ventas"][0]["empleado_id"] = 99

        with self.assertRaisesRegex(ValueError, "empleado_id"):
            _validar_fuentes(fuentes)

    def test_rechaza_categoria_duplicada(self):
        fuentes = fuentes_validas()
        fuentes["categorias"].append({"id": 2, "nombre": "alimentos"})

        with self.assertRaisesRegex(ValueError, "nombres duplicados"):
            _validar_fuentes(fuentes)

    def test_reporta_empleado_incompleto_sin_interrumpir_fuentes(self):
        fuentes = fuentes_validas()
        fuentes["empleados"][0].pop("clave")

        omitidos = _validar_fuentes(fuentes)

        self.assertEqual(omitidos, [(1, 1, "clave")])

    def test_actualizar_cliente_reporta_dni_duplicado(self):
        cliente = Cliente(3, "Ana", "López", "30111222", "")
        duplicado = IntegrityError(msg="Duplicate entry", errno=1062)

        with patch.object(
            RepositorioMySQL, "_ejecutar", side_effect=duplicado
        ):
            with self.assertRaisesRegex(ValueError, "ese DNI"):
                RepositorioMySQL().guardar_cliente(cliente)

    def test_empleado_no_acepta_contrasena_corta(self):
        empleado = {
            "nombre": "Ana López",
            "usuario": "ana",
            "rol": "Administrador"
        }

        with self.assertRaisesRegex(ValueError, "12 caracteres"):
            RepositorioMySQL().guardar_empleado(empleado, "corta")

    def test_empleado_nuevo_requiere_contrasena(self):
        empleado = {
            "nombre": "Ana López",
            "usuario": "ana",
            "rol": "Administrador"
        }

        with self.assertRaisesRegex(ValueError, "es obligatoria"):
            RepositorioMySQL().guardar_empleado(empleado)
