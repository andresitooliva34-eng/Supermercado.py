class Producto:
    
    def __init__(self, id, nombre, categoria, precio, stock):
        # Guarda los datos principales del producto
        self.id = int(id)
        self.nombre = nombre
        self.categoria = categoria
        self.precio = float(precio)
        self.stock = int(stock)


    # Mantiene compatibilidad con código que utiliza id_producto
    @property
    def id_producto(self):
        return self.id


    def hay_stock(self, cantidad):
        # Comprueba si existe stock suficiente
        return self.stock >= cantidad


    def reducir_stock(self, cantidad):
        # Descuenta la cantidad solicitada si hay stock disponible
        if self.hay_stock(cantidad):
            self.stock -= cantidad
            return True

        return False


    # Alias para mantener compatibilidad con código anterior
    descontar_stock = reducir_stock


    def to_dict(self):
        # Convierte el objeto Producto en un diccionario para guardarlo en JSON
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock
        }


    def __str__(self):
        # Define cómo se muestra el producto como texto
        return f"{self.nombre} - ${self.precio} | Stock: {self.stock}"