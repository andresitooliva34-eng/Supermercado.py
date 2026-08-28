from datetime import datetime


class Venta:

    def __init__(self, id, cliente, carrito, metodo_pago):
        # Guarda los datos principales de la venta
        self.id = int(id)
        self.cliente_id = cliente.id
        self.cliente_nombre = cliente.nombre_completo

        # Registra automáticamente la fecha y hora de la venta
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Guarda el medio de pago seleccionado
        self.metodo_pago = metodo_pago

        # Guarda los productos del carrito y calcula cada subtotal
        self.productos = [
            {
                "id": item["producto"].id,
                "nombre": item["producto"].nombre,
                "cantidad": item["cantidad"],
                "precio": item["producto"].precio,
                "subtotal": item["producto"].precio * item["cantidad"]
            }
            for item in carrito.items
        ]

        # Obtiene el total de la compra
        self.total = carrito.calcular_total()


    def finalizar(self):
        # Comprueba que la venta tenga un importe mayor a cero
        return self.total > 0


    def to_dict(self):
        # Convierte la venta en un diccionario para poder guardarla en JSON
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "cliente_nombre": self.cliente_nombre,
            "fecha": self.fecha,
            "productos": self.productos,
            "total": self.total,
            "metodo_pago": self.metodo_pago
        }