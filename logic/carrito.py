class Carrito:
    def __init__(self):
        self.items = []

    def agregar_producto(self, producto, cantidad=1):
        if cantidad <= 0:
            return False

        for item in self.items:
            if item["producto"].id_producto == producto.id_producto:
                nueva_cantidad = item["cantidad"] + cantidad

                if producto.hay_stock(nueva_cantidad):
                    item["cantidad"] = nueva_cantidad
                    return True

                return False

        if producto.hay_stock(cantidad):
            nuevo_item = {
                "producto": producto,
                "cantidad": cantidad
            }
            self.items.append(nuevo_item)
            return True

        return False

    def modificar_cantidad(self, id_producto, nueva_cantidad):
        for item in self.items:
            producto = item["producto"]

            if producto.id_producto == id_producto:
                if nueva_cantidad <= 0:
                    self.eliminar_producto(id_producto)
                    return True

                if producto.hay_stock(nueva_cantidad):
                    item["cantidad"] = nueva_cantidad
                    return True

                return False

        return False

    def eliminar_producto(self, id_producto):
        for item in self.items:
            if item["producto"].id_producto == id_producto:
                self.items.remove(item)
                return True

        return False

    def calcular_total(self):
        return self.calcular_subtotal()

    def calcular_subtotal(self):
        return sum(item["producto"].precio * item["cantidad"] for item in self.items)

    def vaciar_carrito(self):
        self.items.clear()

    vaciar = vaciar_carrito

    def mostrar_productos(self):
        return [
            {"producto": item["producto"], "cantidad": item["cantidad"],
             "subtotal": item["producto"].precio * item["cantidad"]}
            for item in self.items
        ]

    def cantidad_total(self):
        return sum(item["cantidad"] for item in self.items)

    def mostrar_carrito(self):
        if not self.items:
            print("El carrito está vacío.")
            return

        for item in self.items:
            producto = item["producto"]
            cantidad = item["cantidad"]
            subtotal = producto.precio * cantidad

            print(f"{producto.nombre} x{cantidad} = ${subtotal}")

        print(f"Total: ${self.calcular_total()}")
