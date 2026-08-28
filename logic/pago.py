class Pago:
    
    # Método general para procesar un pago
    def pagar(self, total):
        return f"Pago de ${total:,.2f} procesado"

    # Devuelve el total sin modificarlo
    def calcular_total(self, total):
        return total


# Hereda de la clase Pago
class Efectivo(Pago):

    # Sobrescribe el método pagar para pagos en efectivo
    def pagar(self, total):
        return f"Pago en efectivo de ${total:,.2f} registrado"


# Hereda de la clase Pago
class Tarjeta(Pago):

    # Sobrescribe pagar para indicar que se utilizó tarjeta
    def pagar(self, total):
        return f"Pago con tarjeta de ${total:,.2f} aprobado"


# Hereda de la clase Pago
class MercadoPago(Pago):

    # Sobrescribe pagar para indicar que se utilizó Mercado Pago
    def pagar(self, total):
        return f"Pago por Mercado Pago de ${total:,.2f} aprobado"


def crear_pago(metodo):
    # Crea el tipo de pago según el método seleccionado
    return {
        "Efectivo": Efectivo,
        "Tarjeta": Tarjeta,
        "Mercado Pago": MercadoPago
    }.get(metodo, Pago)()