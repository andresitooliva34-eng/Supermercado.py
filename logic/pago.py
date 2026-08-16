class Pago:
    def pagar(self, total):
        return f"Pago de ${total:,.2f} procesado"

    def calcular_total(self, total):
        return total


class Efectivo(Pago):
    def pagar(self, total):
        return f"Pago en efectivo de ${total:,.2f} registrado"


class Tarjeta(Pago):
    def pagar(self, total):
        return f"Pago con tarjeta de ${total:,.2f} aprobado"


class MercadoPago(Pago):
    def pagar(self, total):
        return f"Pago por Mercado Pago de ${total:,.2f} aprobado"


def crear_pago(metodo):
    return {"Efectivo": Efectivo, "Tarjeta": Tarjeta,
            "Mercado Pago": MercadoPago}.get(metodo, Pago)()
