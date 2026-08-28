import json
from pathlib import Path

from logic.producto import Producto
from data.conexion import (
    obtener_productos,
    sincronizar_productos_desde_json,
    actualizar_productos
)


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
        # Carga los productos desde MySQL y utiliza JSON como respaldo
        if not self.ruta_archivo.exists():
            self.ruta_archivo.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            self.ruta_archivo.write_text(
                "[]",
                encoding="utf-8"
            )

        try:
            # MySQL es la fuente principal; JSON permite la carga inicial
            sincronizar_productos_desde_json()
            filas = obtener_productos()

            # Convierte los datos obtenidos de MySQL en diccionarios
            datos = [
                {
                    "id": fila[0],
                    "nombre": fila[1],
                    "categoria": fila[2],
                    "precio": fila[3],
                    "stock": fila[4]
                }
                for fila in filas
            ]

        except Exception:
            # Si MySQL falla, utiliza los datos guardados en JSON
            with open(
                self.ruta_archivo,
                encoding="utf-8"
            ) as archivo:
                datos = json.load(archivo)

        # Vacía la lista antes de volver a cargar los productos
        self.productos.clear()

        # Crea objetos Producto a partir de los datos obtenidos
        for dato in datos:
            producto = Producto(
                dato["id"],
                dato["nombre"],
                dato["categoria"],
                dato["precio"],
                dato["stock"]
            )

            self.productos.append(producto)


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

        # También intenta actualizar los productos en MySQL
        try:
            actualizar_productos(self.productos)
        except Exception:
            # Si MySQL no está disponible, mantiene el JSON actualizado
            pass