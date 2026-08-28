import json
from pathlib import Path


class RepositorioJSON:

    def __init__(self, nombre_archivo):
        # Define la ubicación del archivo JSON
        self.ruta = (
            Path(__file__).resolve().parents[1]
            / "data"
            / nombre_archivo
        )


    def cargar(self):
        # Lee y devuelve los datos almacenados en el archivo JSON
        if not self.ruta.exists():
            # Si el archivo no existe, crea uno vacío
            self.guardar([])

        with open(
            self.ruta,
            encoding="utf-8"
        ) as archivo:
            return json.load(archivo)


    def guardar(self, datos):
        # Crea la carpeta si no existe y guarda los datos en JSON
        self.ruta.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.ruta,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=2
            )