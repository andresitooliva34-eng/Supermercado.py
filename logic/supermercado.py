import json
from pathlib import Path

from logic.producto import Producto
from data.conexion import obtener_productos, sincronizar_productos_desde_json, actualizar_productos


class Supermercado:
    def __init__(self):
        self.productos = []
        self.ruta_archivo = Path(__file__).resolve().parents[1] / "data" / "productos.json"

    def cargar_productos(self):
        if not self.ruta_archivo.exists():
            self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            self.ruta_archivo.write_text("[]", encoding="utf-8")
        try:
            # MySQL es la fuente principal; el JSON aporta la carga inicial.
            sincronizar_productos_desde_json()
            filas = obtener_productos()
            datos = [
                {"id": fila[0], "nombre": fila[1], "categoria": fila[2],
                 "precio": fila[3], "stock": fila[4]}
                for fila in filas
            ]
        except Exception:
            # Permite usar la aplicación aunque MySQL todavía no esté iniciado.
            with open(self.ruta_archivo, encoding="utf-8") as archivo:
                datos = json.load(archivo)

        self.productos.clear()

        for dato in datos:
            producto = Producto(dato["id"], dato["nombre"], dato["categoria"],
                                dato["precio"], dato["stock"])

            self.productos.append(producto)

    def listar_productos(self):
        for producto in self.productos:
            print(producto)

    def buscar_por_nombre(self, texto):
        encontrados = []

        for producto in self.productos:
            if texto.lower() in producto.nombre.lower():
                encontrados.append(producto)

        return encontrados

    def buscar_por_categoria(self, categoria):
        encontrados = []

        for producto in self.productos:
            if categoria.lower() == producto.categoria.lower():
                encontrados.append(producto)

        return encontrados

    def buscar_por_id(self, id_producto):
        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto

        return None

    def agregar_producto(self, producto):
        self.productos.append(producto)

    def siguiente_id(self):
        if not self.productos:
            return 1

        return max(producto.id_producto for producto in self.productos) + 1

    def guardar_productos(self):
        datos = []

        for producto in self.productos:
            datos.append(producto.to_dict())

        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)

        try:
            actualizar_productos(self.productos)
        except Exception:
            pass
