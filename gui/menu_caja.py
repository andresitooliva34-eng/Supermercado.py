import tkinter as tk
from tkinter import messagebox, ttk
from mysql.connector import Error, IntegrityError

from logic.pago import crear_pago
from logic.producto import Producto
from logic.venta import Venta
from gui.exportador_historial import (
    exportar_historial_pdf,
    exportar_historial_excel
)


class CajaMixin:
    """Vistas y acciones del catálogo, cliente, carrito y ventas."""

    def _exportar_historial(self, exportador):
        try:
            ventas = self.repo_ventas.listar_ventas()
        except (Error, FileNotFoundError, ValueError) as error:
            messagebox.showerror(
                "Historial", f"No se pudo cargar el historial:\n{error}",
                parent=self.ventana
            )
            return
        exportador(self.ventana, ventas)

    def _recargar_catalogo(self):
        filas = self.repo_productos.listar_productos()
        self.supermercado.productos = [
            Producto(id_producto, nombre, categoria, precio, stock, codigo)
            for id_producto, codigo, nombre, categoria, precio, stock in filas
        ]

    def cargar_cliente(self):
        return Cliente(0, "Cliente", "General", "", "")

    def guardar_cliente(self):
        if (
            self.cliente.id == 0
            and not self.cliente.dni
            and self.cliente.nombre_completo == "Cliente General"
        ):
            return
        self.repo_clientes.guardar_cliente(self.cliente)

    def actualizar_cliente(self):
        cajero = self.empleado_actual.get("nombre", "") if self.empleado_actual else "Sin sesión"
        self.etiqueta_cliente.config(
            text=(
                f"Cajero: {cajero} | Cliente: "
                f"{self.cliente.nombre_completo}"
            )
        )

    def cambiar_cliente(self):

        v = tk.Toplevel(
            self.ventana
        )

        v.title(
            "Datos del cliente"
        )

        v.resizable(
            False,
            False
        )

        v.transient(self.ventana)
        entradas = []

        datos_cliente = (
            ("Nombre", self.cliente.nombre),
            ("Apellido", self.cliente.apellido),
            ("DNI", self.cliente.dni),
            ("Teléfono", self.cliente.telefono)
        )

        for fila, (texto, valor) in enumerate(
            datos_cliente
        ):

            tk.Label(
                v,
                text=f"{texto}:"
            ).grid(
                row=fila,
                column=0,
                padx=10,
                pady=6,
                sticky="e"
            )

            entrada = tk.Entry(
                v,
                width=30
            )

            entrada.insert(
                0,
                valor
            )

            entrada.grid(
                row=fila,
                column=1,
                padx=10,
                pady=6
            )

            entradas.append(
                entrada
            )

        def guardar():

            if not entradas[0].get().strip():

                messagebox.showwarning(
                    "Cliente",
                    "El nombre es obligatorio.",
                    parent=v
                )

                return

            dni = limpiar_dni(entradas[2].get())
            telefono = entradas[3].get().strip()

            if not dni_valido(dni):

                messagebox.showwarning(
                    "Cliente",
                    "El DNI tiene que tener 7 u 8 números, sin letras.",
                    parent=v
                )

                entradas[2].focus_set()
                return

            if not telefono_valido(telefono):

                messagebox.showwarning(
                    "Cliente",
                    "El teléfono solo puede tener números, espacios, +, - y paréntesis.",
                    parent=v
                )

                entradas[3].focus_set()
                return

            self.cliente.nombre = (
                entradas[0].get().strip()
            )

            self.cliente.apellido = (
                entradas[1].get().strip()
            )

            self.cliente.dni = dni

            self.cliente.telefono = telefono

            try:
                self.guardar_cliente()
            except (Error, IntegrityError, ValueError) as error:
                messagebox.showerror(
                    "Cliente", f"No se pudieron guardar los datos:\n{error}",
                    parent=v
                )
                return
            self.actualizar_cliente()

            v.destroy()

        tk.Button(
            v,
            text="Guardar",
            command=guardar
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            pady=10
        )
        v.after(10, v.grab_set)
        v.focus_set()
        self.ventana.wait_window(v)

    def actualizar_categorias(self):
        categorias = [
            categoria["nombre"]
            for categoria in self.repo_categorias.listar_categorias()
        ]

        self.categoria["values"] = (
            ["Todas"] + categorias
        )

        self.categoria.set(
            "Todas"
        )

    def mostrar_productos(
        self,
        productos=None
    ):

        self.tabla.delete(
            *self.tabla.get_children()
        )

        lista_productos = (
            self.supermercado.productos
            if productos is None
            else productos
        )

        for p in lista_productos:

            estado = (
                "Disponible"
                if p.stock > 0
                else "SIN STOCK"
            )

            self.tabla.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.nombre,
                    p.categoria,
                    f"${p.precio:,.2f}",
                    p.stock,
                    estado
                ),
                tags=(
                    ("sin_stock",)
                    if p.stock == 0
                    else ()
                )
            )

    def filtrar_productos(self):

        texto = (
            self.entrada_busqueda
            .get()
            .strip()
            .lower()
        )

        categoria = (
            self.categoria.get()
        )

        solo_stock = self.solo_stock.get()

        productos_filtrados = [
            p
            for p in self.supermercado.productos
            if texto in p.nombre.lower()
            and (
                categoria == "Todas"
                or p.categoria == categoria
            )
            and (
                not solo_stock
                or p.stock > 0
            )
        ]

        self.mostrar_productos(
            productos_filtrados
        )

    def limpiar_filtros(self):

        self.entrada_busqueda.delete(
            0,
            tk.END
        )

        self.categoria.set(
            "Todas"
        )

        self.solo_stock.set(False)

        self.mostrar_productos()

    def agregar_al_carrito(self):

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Atención",
                "Seleccioná un producto de la tabla."
            )

            return

        id_producto = int(
            self.tabla.item(
                seleccion[0]
            )["values"][0]
        )

        producto = (
            self.supermercado.buscar_por_id(
                id_producto
            )
        )

        cantidad = int(
            self.cantidad.get()
        )

        if self.carrito.agregar_producto(
            producto,
            cantidad
        ):

            self.actualizar_estado()

            messagebox.showinfo(
                "Carrito",
                "Producto agregado al carrito."
            )

        else:

            messagebox.showwarning(
                "Stock",
                "No hay suficiente stock disponible."
            )

    def actualizar_estado(self):

        self.estado.config(
            text=(
                f"🛒 Carrito: "
                f"{self.carrito.cantidad_total()} "
                f"productos  |  "
                f"Total: "
                f"${self.carrito.calcular_total():,.2f}"
            )
        )

    def ver_carrito(self):

        v = tk.Toplevel(
            self.ventana
        )

        v.title(
            "Venta actual"
        )

        v.geometry(
            "610x400"
        )
        v.transient(self.ventana)
        v.wait_visibility()
        v.grab_set()
        v.focus_set()

        tabla = ttk.Treeview(
            v,
            columns=(
                "producto",
                "cantidad",
                "subtotal"
            ),
            show="headings",
            height=11
        )

        for clave, texto in (
            ("producto", "Producto"),
            ("cantidad", "Cant."),
            ("subtotal", "Subtotal")
        ):

            tabla.heading(
                clave,
                text=texto
            )

        tabla.column(
            "producto",
            width=300
        )

        tabla.column(
            "cantidad",
            width=100,
            anchor="center"
        )

        tabla.column(
            "subtotal",
            width=150,
            anchor="e"
        )

        tabla.pack(
            padx=15,
            pady=15,
            fill="x"
        )

        total = tk.Label(
            v,
            font=("Arial", 12, "bold")
        )

        total.pack(
            pady=3
        )


        def recargar():

            tabla.delete(
                *tabla.get_children()
            )

            for item in self.carrito.items:

                producto = item["producto"]
                cantidad = item["cantidad"]

                subtotal = (
                    producto.precio *
                    cantidad
                )

                tabla.insert(
                    "",
                    "end",
                    iid=str(producto.id),
                    values=(
                        producto.nombre,
                        cantidad,
                        f"${subtotal:,.2f}"
                    )
                )

            total.config(
                text=(
                    f"TOTAL: "
                    f"${self.carrito.calcular_total():,.2f}"
                )
            )

            self.actualizar_estado()

        def eliminar():

            seleccion = tabla.selection()

            if seleccion:

                self.carrito.eliminar_producto(
                    int(seleccion[0])
                )

                recargar()

        def modificar():

            seleccion = tabla.selection()

            if not seleccion:
                return

            id_producto = int(
                seleccion[0]
            )

            nueva_cantidad = int(
                spin.get()
            )

            if not self.carrito.modificar_cantidad(
                id_producto,
                nueva_cantidad
            ):

                messagebox.showwarning(
                    "Stock",
                    "Cantidad no disponible.",
                    parent=v
                )

            recargar()

        pie = tk.Frame(v)
        pie.pack(pady=8)

        tk.Label(
            pie,
            text="Cantidad:"
        ).pack(
            side="left"
        )

        spin = tk.Spinbox(
            pie,
            from_=1,
            to=100,
            width=5
        )

        spin.pack(
            side="left",
            padx=4
        )

        tk.Button(
            pie,
            text="Modificar",
            command=modificar
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            pie,
            text="Eliminar",
            command=eliminar
        ).pack(
            side="left",
            padx=4
        )

        tk.Button(
            pie,
            text="Vaciar carrito",
            command=lambda: (
                self.carrito.vaciar(),
                recargar()
            )
        ).pack(
            side="left",
            padx=4
        )

        recargar()
        self.ventana.wait_window(v)

    def finalizar_compra(self):

        if self.empleado_actual is None:
            messagebox.showwarning(
                "Inicio de sesión",
                "Iniciá sesión para registrar una venta."
            )
            self.iniciar_sesion()
            return

        if not self.carrito.items:

            messagebox.showwarning(
                "Carrito",
                "El carrito está vacío."
            )

            return

        d = tk.Toplevel(
            self.ventana
        )

        d.title(
            "Finalizar venta"
        )

        d.resizable(
            False,
            False
        )
        d.grab_set()

        tk.Label(
            d,
            text=(
                f"Total a pagar: "
                f"${self.carrito.calcular_total():,.2f}"
            ),
            font=("Arial", 12, "bold")
        ).pack(
            padx=35,
            pady=(15, 8)
        )

        metodo = tk.StringVar(
            value="Efectivo"
        )

        for opcion in (
            "Efectivo",
            "Tarjeta",
            "Mercado Pago"
        ):

            tk.Radiobutton(
                d,
                text=opcion,
                variable=metodo,
                value=opcion
            ).pack(
                anchor="w",
                padx=35
            )

        def confirmar():

            # 1. Verifica que alcance el stock de TODOS los productos
            for item in self.carrito.items:

                producto = item["producto"]
                cantidad = item["cantidad"]

                if not producto.hay_stock(
                    cantidad
                ):

                    messagebox.showerror(
                        "Stock",
                        f"No hay stock suficiente de {producto.nombre}. Revisá el carrito.",
                        parent=d
                    )

                    return

            try:
                self.guardar_cliente()
                nuevo_id = self.repo_ventas.registrar_venta(
                    self.carrito,
                    self.cliente.id or None,
                    self.empleado_actual["id"],
                    metodo.get()
                )
            except (Error, ValueError) as error:
                messagebox.showerror(
                    "Venta", f"No se pudo registrar la venta:\n{error}",
                    parent=d
                )
                self._recargar_catalogo()
                self.mostrar_productos()
                return

            venta = Venta(
                nuevo_id,
                self.cliente,
                self.carrito,
                metodo.get()
            )
            self.cliente.agregar_compra(venta.id)
            self._recargar_catalogo()

            # Vacía el carrito
            self.carrito.vaciar()

            self.actualizar_estado()
            self.mostrar_productos()

            d.destroy()

            # Procesa el pago según el método elegido
            resultado_pago = crear_pago(
                venta.metodo_pago
            ).pagar(
                venta.total
            )

            messagebox.showinfo(
                "Venta registrada",
                (
                    f"Venta #{venta.id:03d} registrada.\n"
                    f"{resultado_pago}"
                )
            )

        tk.Button(
            d,
            text="Confirmar pago",
            command=confirmar,
            bg="#2E7D32",
            fg="white"
        ).pack(
            pady=15
        )

    def mostrar_historial(self):
        try:
            ventas = self.repo_ventas.listar_ventas()
        except (Error, FileNotFoundError, ValueError) as error:
            messagebox.showerror(
                "Historial", f"No se pudo cargar el historial:\n{error}",
                parent=self.ventana
            )
            return

        v = tk.Toplevel(
            self.ventana
        )

        v.title(
            "Historial de ventas"
        )

        v.geometry(
            "590x330"
        )
        v.transient(self.ventana)
        v.grab_set()   # Captura la interacción (bloquea la ventana principal)
        v.focus_set()  # Le da el foco inicial a la nueva ventana

        tabla = ttk.Treeview(
            v,
            columns=(
                "id",
                "cliente",
                "total",
                "fecha",
                "pago"
            ),
            show="headings",
            height=12
        )

        for clave, texto in (
            ("id", "Venta"),
            ("cliente", "Cliente"),
            ("total", "Total"),
            ("fecha", "Fecha"),
            ("pago", "Pago")
        ):

            tabla.heading(
                clave,
                text=texto
            )

        tabla.column(
            "id",
            width=70,
            anchor="center"
        )

        tabla.column(
            "cliente",
            width=130
        )

        tabla.column(
            "total",
            width=100,
            anchor="e"
        )

        tabla.column(
            "fecha",
            width=140
        )

        tabla.column(
            "pago",
            width=100
        )

        tabla.pack(
            padx=12,
            pady=12,
            fill="both",
            expand=True
        )

        # Muestra primero las ventas más recientes
        for x in reversed(ventas):

            tabla.insert(
                "",
                "end",
                values=(
                    f"#{x['id']:03d}",
                    x.get(
                        "cliente_nombre",
                        ""
                    ),
                    f"${x['total']:,.2f}",
                    x["fecha"],
                    x["metodo_pago"]
                )
            )
