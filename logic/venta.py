from datetime import datetime


class Venta:
    def __init__(self, id, cliente, carrito, metodo_pago):
        self.id = int(id)
        self.cliente_id = cliente.id
        self.cliente_nombre = cliente.nombre_completo
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.metodo_pago = metodo_pago
        self.productos = [
            {"id": item["producto"].id, "nombre": item["producto"].nombre,
             "cantidad": item["cantidad"], "precio": item["producto"].precio,
             "subtotal": item["producto"].precio * item["cantidad"]}
            for item in carrito.items
        ]
        self.total = carrito.calcular_total()

    def finalizar(self):
        return self.total > 0

    def to_dict(self):
        return {"id": self.id, "cliente_id": self.cliente_id,
                "cliente_nombre": self.cliente_nombre, "fecha": self.fecha,
                "productos": self.productos, "total": self.total,
                "metodo_pago": self.metodo_pago}
