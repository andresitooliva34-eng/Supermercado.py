import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from data import conexion


class CargarConfiguracionTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.ruta_config = Path(self.directorio.name) / "config_db.json"
        self.config_patch = patch.object(conexion, "RUTA_CONFIG", self.ruta_config)
        self.config_patch.start()
        self.entorno_patch = patch.dict(os.environ, {}, clear=True)
        self.entorno_patch.start()

    def tearDown(self):
        self.entorno_patch.stop()
        self.config_patch.stop()
        self.directorio.cleanup()

    def escribir_config(self, datos):
        self.ruta_config.write_text(json.dumps(datos), encoding="utf-8")

    def test_carga_configuracion_local_y_puerto_por_defecto(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_cajero",
            "password": "secreto-cajero",
            "database": "codemarket"
        })

        configuracion = conexion.cargar_configuracion()

        self.assertEqual(configuracion["port"], 3306)
        self.assertEqual(configuracion["user"], "cm_cajero")
        self.assertEqual(configuracion["password"], "secreto-cajero")

    def test_rechaza_marcador_de_contrasena_sin_configurar(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_cajero",
            "password": "CONFIGURAR_LOCALMENTE",
            "database": "codemarket"
        })

        with self.assertRaisesRegex(ValueError, "CONFIGURAR_LOCALMENTE"):
            conexion.cargar_configuracion()

    def test_rechaza_puerto_fuera_de_rango(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_cajero",
            "password": "secreto-local",
            "database": "codemarket",
            "port": 70000
        })

        with self.assertRaisesRegex(ValueError, "entre 1 y 65535"):
            conexion.cargar_configuracion()

    def test_rechaza_puerto_decimal(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_cajero",
            "password": "secreto-local",
            "database": "codemarket",
            "port": 3306.5
        })

        with self.assertRaisesRegex(ValueError, "número entero"):
            conexion.cargar_configuracion()

    def test_credenciales_administrativas_solo_seleccionan_cm_admin(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_cajero",
            "password": "secreto-cajero",
            "admin_user": "cm_admin",
            "admin_password": "secreto-admin",
            "database": "codemarket"
        })

        configuracion = conexion.cargar_configuracion(administrativa=True)

        self.assertEqual(configuracion["user"], "cm_admin")
        self.assertEqual(configuracion["password"], "secreto-admin")

    def test_rechaza_cm_admin_como_usuario_operativo(self):
        self.escribir_config({
            "host": "localhost",
            "user": "cm_admin",
            "password": "secreto-admin",
            "database": "codemarket"
        })

        with self.assertRaisesRegex(ValueError, "debe usar cm_cajero"):
            conexion.cargar_configuracion()
