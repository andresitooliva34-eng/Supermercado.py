import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from logic.carrito import Carrito
from logic.cliente import Cliente
from logic.pago import crear_pago
from logic.repositorio import RepositorioJSON
from logic.supermercado import Supermercado
from logic.venta import Venta

from gui.exportador_historial import (
    exportar_historial_pdf,
    exportar_historial_excel
)


def ruta_recurso(relativa):
    """
    Devuelve la ruta correcta de un recurso.
    Funciona tanto ejecutando con Python como con un .exe.
    """
    base = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    return os.path.join(base, relativa)


class VentanaSupermercado:

    def __init__(self, ventana):

        # Configuración principal de la ventana
        self.ventana = ventana
        ventana.title("Supermercado | Gestión de compras")
        ventana.iconbitmap(
            ruta_recurso("assets/supermercado_icon.ico")
        )
        ventana.geometry("920x590")
        ventana.configure(bg="#F1F8E9")

        # Carga de productos
        self.supermercado = Supermercado()
        self.supermercado.cargar_productos()

        # Creación del carrito
        self.carrito = Carrito()

        # Repositorios JSON
        self.repo_clientes = RepositorioJSON("clientes.json")
        self.repo_ventas = RepositorioJSON("ventas.json")

        # Carga del cliente activo
        self.cliente = self.cargar_cliente()

        # Menú superior
        self._crear_menu_archivo()

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        tk.Label(
            ventana,
            text="🛒 SUPERMERCADO 🛒",
            font=("Arial", 22, "bold"),
            bg="#F1F8E9",
            fg="#2E7D32"
        ).pack(pady=(14, 2))

        tk.Label(
            ventana,
            text="Tu changuito de compras, más fácil",
            font=("Arial", 10, "italic"),
            bg="#F1F8E9",
            fg="#558B2F"
        ).pack(pady=(0, 8))

        tk.Frame(
            ventana,
            bg="#A5D6A7",
            height=2
        ).pack(
            fill="x",
            padx=60,
            pady=(0, 6)
        )

        # Cliente activo
        self.etiqueta_cliente = tk.Label(
            ventana,
            bg="#F1F8E9"
        )
        self.etiqueta_cliente.pack()

        # --------------------------------------------------
        # FILTROS
        # --------------------------------------------------

        filtros = tk.Frame(
            ventana,
            bg="#F1F8E9"
        )
        filtros.pack(pady=9)

        tk.Label(
            filtros,
            text="🔎 Buscar por nombre:",
            bg="#F1F8E9"
        ).grid(row=0, column=0)

        self.entrada_busqueda = tk.Entry(
            filtros,
            width=26
        )
        self.entrada_busqueda.grid(
            row=0,
            column=1,
            padx=(5, 18)
        )

        self.entrada_busqueda.bind(
            "<KeyRelease>",
            lambda _e: self.filtrar_productos()
        )

        tk.Label(
            filtros,
            text="📂 Categoría:",
            bg="#F1F8E9"
        ).grid(row=0, column=2)

        self.categoria = ttk.Combobox(
            filtros,
            state="readonly",
            width=17
        )

        self.categoria.grid(
            row=0,
            column=3,
            padx=5
        )

        self.categoria.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.filtrar_productos()
        )

        self._crear_boton_accion(
            filtros,
            "🧹 Limpiar filtros",
            self.limpiar_filtros
        ).grid(
            row=0,
            column=4,
            padx=8
        )

        # --------------------------------------------------
        # ESTILO DE LA TABLA
        # --------------------------------------------------

        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview.Heading",
            background="#2E7D32",
            foreground="white",
            font=("Arial", 9, "bold")
        )

        estilo.map(
            "Treeview.Heading",
            background=[
                ("active", "#388E3C")
            ]
        )

        estilo.configure(
            "Treeview",
            rowheight=24,
            font=("Arial", 9)
        )

        # --------------------------------------------------
        # TABLA DE PRODUCTOS
        # --------------------------------------------------

        columnas = (
            "id",
            "nombre",
            "categoria",
            "precio",
            "stock",
            "estado"
        )

        self.tabla = ttk.Treeview(
            ventana,
            columns=columnas,
            show="headings",
            height=13
        )

        for clave, texto in zip(
            columnas,
            (
                "ID",
                "Producto",
                "Categoría",
                "Precio",
                "Stock",
                "Estado"
            )
        ):
            self.tabla.heading(
                clave,
                text=texto
            )

        configuracion_columnas = (
            ("id", 45, "center"),
            ("nombre", 240, "w"),
            ("categoria", 145, "w"),
            ("precio", 115, "e"),
            ("stock", 70, "center"),
            ("estado", 115, "center")
        )

        for clave, ancho, alineacion in configuracion_columnas:
            self.tabla.column(
                clave,
                width=ancho,
                anchor=alineacion
            )

        self.tabla.tag_configure(
            "sin_stock",
            foreground="#B71C1C"
        )

        self.tabla.pack(
            padx=20,
            pady=4,
            fill="x"
        )

        # --------------------------------------------------
        # ACCIONES
        # --------------------------------------------------

        acciones = tk.Frame(
            ventana,
            bg="#F1F8E9"
        )
        acciones.pack(pady=10)

        tk.Label(
            acciones,
            text="Cantidad:",
            bg="#F1F8E9"
        ).pack(side="left")

        self.cantidad = tk.Spinbox(
            acciones,
            from_=1,
            to=100,
            width=5
        )
        self.cantidad.pack(
            side="left",
            padx=6
        )

        botones_info = (
            (
                "🛒 Agregar al carrito",
                self.agregar_al_carrito,
                True
            ),
            (
                "👁 Ver carrito",
                self.ver_carrito,
                False
            ),
            (
                "💳 Finalizar compra",
                self.finalizar_compra,
                False
            ),
            (
                "📜 Historial",
                self.mostrar_historial,
                False
            ),
            (
                "👤 Cambiar cliente",
                self.cambiar_cliente,
                False
            ),
        )

        for texto, comando, destacado in botones_info:

            self._crear_boton_accion(
                acciones,
                texto,
                comando,
                destacado
            ).pack(
                side="left",
                padx=4
            )

        self.estado = tk.Label(
            ventana,
            bg="#F1F8E9",
            font=("Arial", 10, "bold"),
            fg="#2E7D32"
        )

        self.estado.pack(pady=4)

        # Actualización inicial de la interfaz
        self.actualizar_cliente()
        self.actualizar_categorias()
        self.mostrar_productos()
        self.actualizar_estado()

    # ------------------------------------------------------
    # BOTONES
    # ------------------------------------------------------

    @staticmethod
    def _aplicar_hover(
        boton,
        color_normal,
        color_hover
    ):
        boton.bind(
            "<Enter>",
            lambda e: boton.config(
                bg=color_hover
            )
        )

        boton.bind(
            "<Leave>",
            lambda e: boton.config(
                bg=color_normal
            )
        )

    def _crear_boton_accion(
        self,
        padre,
        texto,
        comando,
        destacado=False
    ):

        color_normal = (
            "#2E7D32"
            if destacado
            else "#558B2F"
        )

        color_hover = (
            "#388E3C"
            if destacado
            else "#689F38"
        )

        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color_normal,
            fg="white",
            font=("Arial", 9, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4
        )

        self._aplicar_hover(
            boton,
            color_normal,
            color_hover
        )

        return boton

    # ------------------------------------------------------
    # MENÚ
    # ------------------------------------------------------

    def _crear_menu_archivo(self):

        barra_menu = tk.Menu(
            self.ventana
        )

        self.ventana.config(
            menu=barra_menu
        )

        self.barra_menu = barra_menu

        menu_archivo = tk.Menu(
            barra_menu,
            tearoff=0
        )

        menu_archivo.add_command(
            label="Exportar Historial a PDF",
            command=lambda:
                exportar_historial_pdf(
                    self.ventana,
                    self.repo_ventas.cargar()
                )
        )

        menu_archivo.add_command(
            label="Exportar Historial a Excel",
            command=lambda:
                exportar_historial_excel(
                    self.ventana,
                    self.repo_ventas.cargar()
                )
        )

        menu_archivo.add_separator()

        menu_archivo.add_command(
            label="Salir",
            command=self.ventana.quit
        )

        barra_menu.add_cascade(
            label="Archivo",
            menu=menu_archivo
        )

        menu_acerca = tk.Menu(
            barra_menu,
            tearoff=0
        )

        menu_acerca.add_command(
            label="Acerca de Supermercado",
            command=self._mostrar_acerca_de
        )

        barra_menu.add_cascade(
            label="Acerca de",
            menu=menu_acerca
        )

    # ------------------------------------------------------
    # ACERCA DE
    # ------------------------------------------------------

    def _mostrar_acerca_de(self):

        ventana_acerca = tk.Toplevel(
            self.ventana
        )

        ventana_acerca.title(
            "Acerca de Supermercado"
        )

        ventana_acerca.geometry(
            "420x460"
        )

        ventana_acerca.configure(
            bg="#F1F8E9"
        )

        ventana_acerca.resizable(
            False,
            False
        )

        ventana_acerca.grab_set()

        tk.Label(
            ventana_acerca,
            text="SUPERMERCADO",
            font=("Arial", 20, "bold"),
            bg="#F1F8E9",
            fg="#2E7D32"
        ).pack(pady=(25, 0))

        tk.Label(
            ventana_acerca,
            text="Sistema de Gestión de Compras",
            font=("Arial", 10, "italic"),
            bg="#F1F8E9",
            fg="#558B2F"
        ).pack(pady=(0, 15))

        tk.Frame(
            ventana_acerca,
            bg="#558B2F",
            height=1
        ).pack(
            fill="x",
            padx=40,
            pady=(0, 15)
        )

        tk.Label(
            ventana_acerca,
            text="Proyecto académico",
            font=("Arial", 10),
            bg="#F1F8E9",
            fg="#2E7D32"
        ).pack()

        tk.Label(
            ventana_acerca,
            text=(
                "Tecnicatura Superior en Desarrollo de Software\n"
                "Instituto Superior Politécnico Córdoba (ISPC)"
            ),
            font=("Arial", 9, "italic"),
            bg="#F1F8E9",
            fg="#558B2F",
            justify="center"
        ).pack(
            pady=(2, 15)
        )

        tk.Label(
            ventana_acerca,
            text="Integrantes:",
            font=("Arial", 11, "bold"),
            bg="#F1F8E9",
            fg="#2E7D32"
        ).pack(
            pady=(0, 8)
        )

        integrantes = [
            "Lozano Bazán, Facundo Nicolás",
            "Marín Silva, Rafael Alejandro",
            "Oliva Ruiz, Roberto Andrés",
            "Roldán, Gabriel",
            "Saravia, Samuel Eric",
            "Espeche, Brenda Aylen",
        ]

        for nombre in integrantes:

            tk.Label(
                ventana_acerca,
                text=f"•  {nombre}",
                font=("Arial", 10),
                bg="#F1F8E9",
                fg="#33691E",
                anchor="w"
            ).pack(
                fill="x",
                padx=55,
                pady=1
            )

        tk.Button(
            ventana_acerca,
            text="Cerrar",
            command=ventana_acerca.destroy,
            bg="#2E7D32",
            fg="white",
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            width=12
        ).pack(
            pady=20
        )

    # ------------------------------------------------------
    # CLIENTE
    # ------------------------------------------------------

    def cargar_cliente(self):
        # Carga el cliente guardado en JSON
        datos = self.repo_clientes.cargar()

        if datos:

            d = datos[0]

            cliente = Cliente(
                d["id"],
                d["nombre"],
                d.get("apellido", ""),
                d.get("email", "")
            )

            cliente.historial_compras = d.get(
                "historial_compras",
                []
            )

            return cliente

        # Si no existe cliente, crea uno general
        cliente = Cliente(
            1,
            "Cliente",
            "General",
            ""
        )

        self.repo_clientes.guardar(
            [cliente.to_dict()]
        )

        return cliente

    def guardar_cliente(self):
        self.repo_clientes.guardar(
            [self.cliente.to_dict()]
        )

    def actualizar_cliente(self):
        self.etiqueta_cliente.config(
            text=(
                f"Cliente activo: "
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

        entradas = []

        datos_cliente = (
            ("Nombre", self.cliente.nombre),
            ("Apellido", self.cliente.apellido),
            ("Email", self.cliente.email)
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

            self.cliente.nombre = (
                entradas[0].get().strip()
            )

            self.cliente.apellido = (
                entradas[1].get().strip()
            )

            self.cliente.email = (
                entradas[2].get().strip()
            )

            self.guardar_cliente()
            self.actualizar_cliente()

            v.destroy()

        tk.Button(
            v,
            text="Guardar",
            command=guardar
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            pady=10
        )

    # ------------------------------------------------------
    # PRODUCTOS
    # ------------------------------------------------------

    def actualizar_categorias(self):

        categorias = sorted(
            {
                p.categoria
                for p in self.supermercado.productos
            }
        )

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

        productos_filtrados = [
            p
            for p in self.supermercado.productos
            if texto in p.nombre.lower()
            and (
                categoria == "Todas"
                or p.categoria == categoria
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

        self.mostrar_productos()

    # ------------------------------------------------------
    # CARRITO
    # ------------------------------------------------------

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
            "Mi carrito"
        )

        v.geometry(
            "610x400"
        )

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

    # ------------------------------------------------------
    # FINALIZAR COMPRA
    # ------------------------------------------------------

    def finalizar_compra(self):

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
            "Finalizar compra"
        )

        d.resizable(
            False,
            False
        )

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

            # Verifica y descuenta el stock
            for item in self.carrito.items:

                producto = item["producto"]
                cantidad = item["cantidad"]

                if not producto.reducir_stock(
                    cantidad
                ):

                    messagebox.showerror(
                        "Stock",
                        "El stock cambió. Revisá el carrito.",
                        parent=d
                    )

                    return

            # Obtiene las ventas existentes
            datos = self.repo_ventas.cargar()

            # Genera un nuevo ID para la venta
            nuevo_id = (
                max(
                    (
                        x["id"]
                        for x in datos
                    ),
                    default=0
                ) + 1
            )

            # Crea el objeto Venta
            venta = Venta(
                nuevo_id,
                self.cliente,
                self.carrito,
                metodo.get()
            )

            # Guarda la venta
            datos.append(
                venta.to_dict()
            )

            self.repo_ventas.guardar(
                datos
            )

            # Actualiza el historial del cliente
            self.cliente.agregar_compra(
                venta.id
            )

            self.guardar_cliente()

            # Guarda el nuevo stock
            self.supermercado.guardar_productos()

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
                "Compra realizada",
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

    # ------------------------------------------------------
    # HISTORIAL
    # ------------------------------------------------------

    def mostrar_historial(self):

        ventas = self.repo_ventas.cargar()

        v = tk.Toplevel(
            self.ventana
        )

        v.title(
            "Historial de compras"
        )

        v.geometry(
            "590x330"
        )

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


# ----------------------------------------------------------
# INICIO DE LA INTERFAZ
# ----------------------------------------------------------

def iniciar_interfaz():
    ventana = tk.Tk()

    VentanaSupermercado(
        ventana
    )

    ventana.mainloop()