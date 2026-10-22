import re
import unittest
from pathlib import Path

import bcrypt


class CredencialesDemoTests(unittest.TestCase):
    def test_hash_de_la_cuenta_demo_corresponde_al_login_visible(self):
        ruta = Path(__file__).resolve().parents[1] / "data" / "demo_admin.sql"
        sql = ruta.read_text(encoding="utf-8")
        hash_clave = re.search(r"'(\$2[aby]\$[^']+)'", sql).group(1)

        self.assertTrue(
            bcrypt.checkpw(b"admin123", hash_clave.encode("ascii"))
        )

    def test_esquema_nuevo_crea_la_cuenta_demo_activa(self):
        ruta = Path(__file__).resolve().parents[1] / "data" / "schema.sql"
        sql = ruta.read_text(encoding="utf-8")

        self.assertIn("'admin', 'administrador'", sql)
        self.assertIn("admin / admin123", sql)
        self.assertIn("1),", sql)
