class Carrito:
    
    def __init__(self):
        # Lista donde se guardan los productos seleccionados
        self.items = []


    def agregar_producto(self, producto, cantidad=1):
        # Agrega un producto al carrito verificando el stock
        if cantidad <= 0:
            return False

        # Si el producto ya está en el carrito, aumenta su cantidad
        for item in self.items:
            if item["producto"].id_producto == producto.id_producto:
                nueva_cantidad = item["cantidad"] + cantidad

                if producto.hay_stock(nueva_cantidad):
                    item["cantidad"] = nueva_cantidad
                    return True

                return False

        # Si es un producto nuevo, verifica que haya stock
        if producto.hay_stock(cantidad):
            nuevo_item = {
                "producto": producto,
                "cantidad": cantidad
            }

            self.items.append(nuevo_item)
            return True

        return False


    def modificar_cantidad(self, id_producto, nueva_cantidad):
        # Busca el producto y modifica la cantidad solicitada
        for item in self.items:
            producto = item["producto"]

            if producto.id_producto == id_producto:

                # Si la cantidad es 0 o menor, elimina el producto
                if nueva_cantidad <= 0:
                    self.eliminar_producto(id_producto)
                    return True

                # Verifica el stock antes de modificar
                if producto.hay_stock(nueva_cantidad):
                    item["cantidad"] = nueva_cantidad
                    return True

                return False

        return False


    def eliminar_producto(self, id_producto):
        # Busca y elimina un producto del carrito
        for item in self.items:
            if item["producto"].id_producto == id_producto:
                self.items.remove(item)
                return True

        return False


    def calcular_total(self):
        # Devuelve el total de la compra
        return self.calcular_subtotal()


    def calcular_subtotal(self):
        # Suma precio × cantidad de todos los productos
        return sum(
            item["producto"].precio * item["cantidad"]
            for item in self.items
        )


    def vaciar_carrito(self):
        # Elimina todos los productos del carrito
        self.items.clear()


    # Alias para poder utilizar también el nombre "vaciar"
    vaciar = vaciar_carrito


    def mostrar_productos(self):
        # Devuelve los productos con cantidad y subtotal
        return [
            {
                "producto": item["producto"],
                "cantidad": item["cantidad"],
                "subtotal": (
                    item["producto"].precio *
                    item["cantidad"]
                )
            }
            for item in self.items
        ]


    def cantidad_total(self):
        # Calcula la cantidad total de unidades del carrito
        return sum(
            item["cantidad"]
            for item in self.items
        )


    def mostrar_carrito(self):
        # Muestra el contenido del carrito por consola
        if not self.items:
            print("El carrito está vacío.")
            return

        for item in self.items:
            producto = item["producto"]
            cantidad = item["cantidad"]
            subtotal = producto.precio * cantidad

            print(
                f"{producto.nombre} x{cantidad} = ${subtotal}"
            )

        print(
            f"Total: ${self.calcular_total()}"
        )