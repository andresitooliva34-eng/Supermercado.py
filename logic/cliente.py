class Cliente:
    
    def __init__(self, id, nombre, apellido="", email=""):
        # Guarda los datos principales del cliente
        self.id = int(id)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

        # Guarda los IDs de las compras realizadas
        self.historial_compras = []


    @property
    def nombre_completo(self):
        # Devuelve el nombre y apellido juntos
        return f"{self.nombre} {self.apellido}".strip()


    def agregar_compra(self, venta_id):
        # Agrega una venta al historial del cliente
        self.historial_compras.append(venta_id)


    def to_dict(self):
        # Convierte el cliente en un diccionario para guardarlo en JSON
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "historial_compras": self.historial_compras
        }