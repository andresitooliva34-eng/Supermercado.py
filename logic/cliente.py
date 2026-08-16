class Cliente:
    def __init__(self, id, nombre, apellido="", email=""):
        self.id = int(id)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.historial_compras = []

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    def agregar_compra(self, venta_id):
        self.historial_compras.append(venta_id)

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre, "apellido": self.apellido,
                "email": self.email, "historial_compras": self.historial_compras}
