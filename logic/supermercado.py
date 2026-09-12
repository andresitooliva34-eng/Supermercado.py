import json
from pathlib import Path

from logic.producto import Producto


class Supermercado:

    def __init__(self):
        # Lista donde se almacenan los productos del supermercado
        self.productos = []

        # Define la ubicación del archivo JSON de productos
        self.ruta_archivo = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "productos.json"
        )


    def cargar_productos(self):
        # Carga los productos desde el archivo JSON
        if not self.ruta_archivo.exists():
            self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            self.ruta_archivo.write_text("[]", encoding="utf-8")

        with open(self.ruta_archivo, encoding="utf-8") as archivo:
            datos = json.load(archivo)

        self.productos.clear()

        for dato in datos:
            self.productos.append(
                Producto(
                    dato["id"],
                    dato["nombre"],
                    dato["categoria"],
                    dato["precio"],
                    dato["stock"]
                )
            )


    def listar_productos(self):
        # Muestra todos los productos por consola
        for producto in self.productos:
            print(producto)


    def buscar_por_nombre(self, texto):
        # Busca productos cuyo nombre contenga el texto ingresado
        encontrados = []

        for producto in self.productos:
            if texto.lower() in producto.nombre.lower():
                encontrados.append(producto)

        return encontrados


    def buscar_por_categoria(self, categoria):
        # Devuelve los productos que pertenecen a una categoría
        encontrados = []

        for producto in self.productos:
            if categoria.lower() == producto.categoria.lower():
                encontrados.append(producto)

        return encontrados


    def buscar_por_id(self, id_producto):
        # Busca un producto específico mediante su ID
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto

        return None


    def agregar_producto(self, producto):
        # Agrega un nuevo producto a la lista
        self.productos.append(producto)


    def siguiente_id(self):
        # Calcula el próximo ID disponible para un producto
        if not self.productos:
            return 1

        return max(
            producto.id_producto
            for producto in self.productos
        ) + 1


    def guardar_productos(self):
        # Convierte los productos a diccionarios para guardarlos en JSON
        datos = []

        for producto in self.productos:
            datos.append(producto.to_dict())

        with open(
            self.ruta_archivo,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=2
            )