class Producto:
    def __init__(self, id, nombre, categoria, precio, stock):
        self.id = int(id)
        self.nombre = nombre
        self.categoria = categoria
        self.precio = float(precio)
        self.stock = int(stock)

    # Mantiene compatibilidad con el código anterior.
    @property
    def id_producto(self):
        return self.id

    def hay_stock(self, cantidad):
        return self.stock >= cantidad

    def reducir_stock(self, cantidad):
        if self.hay_stock(cantidad):
            self.stock -= cantidad
            return True
        return False

    descontar_stock = reducir_stock

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "categoria": self.categoria,
                "precio": self.precio, "stock": self.stock}

    def __str__(self):
        return f"{self.nombre} - ${self.precio} | Stock: {self.stock}"
