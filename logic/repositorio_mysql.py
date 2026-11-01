"""Compatibility facade for callers migrating to entity repositories."""

from logic.repositorio_categorias import RepositorioCategoriasMySQL
from logic.repositorio_clientes import RepositorioClientesMySQL
from logic.repositorio_empleados import RepositorioEmpleadosMySQL
from logic.repositorio_ventas import RepositorioVentasMySQL


class RepositorioMySQL:
    """Delegates the former aggregate API to repositories by entity."""

    def __init__(self):
        self.categorias = RepositorioCategoriasMySQL()
        self.clientes = RepositorioClientesMySQL()
        self.empleados = RepositorioEmpleadosMySQL()
        self.ventas = RepositorioVentasMySQL()

    def listar_categorias(self):
        return self.categorias.listar_categorias()

    def guardar_categoria(self, categoria):
        return self.categorias.guardar_categoria(categoria)

    def eliminar_categoria(self, id_categoria):
        return self.categorias.eliminar_categoria(id_categoria)

    def listar_clientes(self):
        return self.clientes.listar_clientes()

    def guardar_cliente(self, cliente):
        if isinstance(cliente, dict):
            return self.clientes.guardar_cliente_registro(cliente)
        return self.clientes.guardar_cliente(cliente)

    def eliminar_cliente(self, id_cliente):
        return self.clientes.eliminar_cliente(id_cliente)

    def listar_empleados(self):
        return self.empleados.listar_empleados()

    def autenticar_empleado(self, usuario, clave):
        return self.empleados.autenticar_empleado(usuario, clave)

    def guardar_empleado(self, empleado, clave=None):
        return self.empleados.guardar_empleado(empleado, clave)

    def eliminar_empleado(self, id_empleado):
        return self.empleados.eliminar_empleado(id_empleado)

    def listar_ventas(self):
        return self.ventas.listar_ventas()

    def registrar_venta(self, carrito, cliente_id, empleado_id, metodo_pago):
        return self.ventas.registrar_venta(
            carrito, cliente_id, empleado_id, metodo_pago
        )

    def importar_venta_legacy(
        self, venta, id_cliente, id_empleado, productos, id_origen
    ):
        return self.ventas.importar_venta_legacy(
            venta, id_cliente, id_empleado, productos, id_origen
        )
