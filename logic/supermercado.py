class Supermercado:

    def __init__(self):
        # Catálogo en memoria cargado por la interfaz desde MySQL.
        self.productos = []

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
        # Busca un producto específico mediante su ID de forma segura
        for producto in self.productos:
            p_id = getattr(producto, "id", getattr(producto, "id_producto", None))
            if p_id == id_producto:
                return producto

        return None


    def agregar_producto(self, producto):
        # Agrega un nuevo producto a la lista
        self.productos.append(producto)


    def actualizar_producto(self, id_producto, nombre, categoria, precio, stock):
        producto = self.buscar_por_id(int(id_producto))
        if producto is None:
            return False
        producto.nombre = nombre
        producto.categoria = categoria
        producto.precio = float(precio)
        producto.stock = int(stock)
        return True


    def eliminar_producto(self, id_producto):
        producto = self.buscar_por_id(int(id_producto))
        if producto is None:
            return False
        self.productos.remove(producto)
        return True


    def siguiente_id(self):
        # Calcula el próximo ID disponible para un producto
        if not self.productos:
            return 1

        return max(
            getattr(p, "id", getattr(p, "id_producto", 0))
            for p in self.productos
        ) + 1
