import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from mysql.connector import Error

from logic.carrito import Carrito
from gui.menu_administracion import AdministracionMixin
from gui.menu_caja import CajaMixin
from logic.repositorio_categorias import RepositorioCategoriasMySQL
from logic.repositorio_clientes import RepositorioClientesMySQL
from logic.repositorio_empleados import RepositorioEmpleadosMySQL
from logic.repositorio_productos import RepositorioProductosMySQL
from logic.repositorio_ventas import RepositorioVentasMySQL
from logic.supermercado import Supermercado
from gui.exportador_historial import (
    exportar_historial_excel,
    exportar_historial_pdf
)
from gui.ventana_productos import VentanaProductos


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


class VentanaSupermercado(AdministracionMixin, CajaMixin):

    def __init__(self, ventana):

        # Configuración principal de la ventana
        self.ventana = ventana
        ventana.title("Supermercado | Caja y administración")
        ventana.iconbitmap(
            ruta_recurso("assets/supermercado_icon.ico")
        )
        ventana.geometry("1100x700")
        ventana.minsize(980, 620)
        ventana.configure(bg="#F1F8E9")

        # Pide confirmación antes de cerrar la aplicación
        ventana.protocol(
            "WM_DELETE_WINDOW",
            self._al_cerrar
        )

        # Todos los datos operativos se almacenan en MySQL.
        self.supermercado = Supermercado()
        self.repo_categorias = RepositorioCategoriasMySQL()
        self.repo_clientes = RepositorioClientesMySQL()
        self.repo_empleados = RepositorioEmpleadosMySQL()
        self.repo_productos = RepositorioProductosMySQL()
        self.repo_ventas = RepositorioVentasMySQL()
        self._recargar_catalogo()

        # Creación del carrito
        self.carrito = Carrito()

        self.empleado_actual = None

        # Carga del cliente activo
        self.cliente = self.cargar_cliente()

        # Menú superior
        self._crear_menu_archivo()

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        tk.Label(
            ventana,
            text="SUPERMERCADO | PUNTO DE VENTA",
            font=("Arial", 22, "bold"),
            bg="#F1F8E9",
            fg="#2E7D32"
        ).pack(pady=(14, 2))

        tk.Label(
            ventana,
            text="Caja para registrar ventas y administrar el negocio",
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
        # FILTROS:
        # --------------------------------------------------

        filtros = tk.LabelFrame(
            ventana,
            text="Filtros de búsqueda",
            bg="#F1F8E9",
            fg="#2E7D32",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=8
        )
        filtros.pack(pady=9, padx=20, fill="x")

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

        # Filtro adicional: mostrar solo productos con stock disponible
        self.solo_stock = tk.BooleanVar(value=False)

        tk.Checkbutton(
            filtros,
            text="Solo con stock",
            variable=self.solo_stock,
            bg="#F1F8E9",
            command=self.filtrar_productos
        ).grid(
            row=0,
            column=4,
            padx=8
        )

        self._crear_boton_accion(
            filtros,
            "🧹 Limpiar filtros",
            self.limpiar_filtros
        ).grid(
            row=0,
            column=5,
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

        contenedor_tabla = tk.Frame(
            ventana,
            bg="#F1F8E9"
        )
        contenedor_tabla.pack(
            padx=20,
            pady=4,
            fill="both",
            expand=True
        )

        self.tabla = ttk.Treeview(
            contenedor_tabla,
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

        scroll_tabla = tk.Scrollbar(
            contenedor_tabla,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.config(
            yscrollcommand=scroll_tabla.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scroll_tabla.pack(
            side="right",
            fill="y"
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
                "Agregar producto",
                self.agregar_al_carrito,
                True
            ),
            (
                "👁 Ver carrito",
                self.ver_carrito,
                False
            ),
            (
                "Finalizar venta",
                self.finalizar_compra,
                False
            ),
            (
                "📜 Historial",
                self.mostrar_historial,
                False
            ),
            (
                "Datos del cliente",
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
        self.ventana.after(150, self.iniciar_sesion)

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
            "#687554"
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
            command=lambda: self._exportar_historial(exportar_historial_pdf)
        )

        menu_archivo.add_command(
            label="Exportar Historial a Excel",
            command=lambda: self._exportar_historial(exportar_historial_excel)
        )

        menu_archivo.add_command(
            label="Productos (MySQL)",
            command=lambda: VentanaProductos(self.ventana)
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

        self.menu_administracion = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Administracion", menu=self.menu_administracion)
        self._actualizar_menu_administracion()

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
    # CERRAR APLICACIÓN
    # ------------------------------------------------------

    def _al_cerrar(self):

        if messagebox.askyesno(
            "Salir",
            "¿Cerrar la aplicación?"
        ):

            self.ventana.destroy()
    # ------------------------------------------------------
    # FINALIZAR COMPRA
    # ------------------------------------------------------


    # ------------------------------------------------------
    # HISTORIAL
    # ------------------------------------------------------



# ----------------------------------------------------------
# INICIO DE LA INTERFAZ
# ----------------------------------------------------------

def iniciar_interfaz():
    ventana = tk.Tk()

    try:
        VentanaSupermercado(ventana)
    except (Error, FileNotFoundError, ValueError) as error:
        messagebox.showerror(
            "Base de datos",
            f"No se pudo iniciar la aplicación con MySQL:\n{error}",
            parent=ventana
        )
        ventana.destroy()
        return

    ventana.mainloop()