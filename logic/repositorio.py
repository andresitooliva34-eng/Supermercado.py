import json
from pathlib import Path


class RepositorioJSON:
    def __init__(self, nombre_archivo):
        self.ruta = Path(__file__).resolve().parents[1] / "data" / nombre_archivo

    def cargar(self):
        if not self.ruta.exists():
            self.guardar([])
        with open(self.ruta, encoding="utf-8") as archivo:
            return json.load(archivo)

    def guardar(self, datos):
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
