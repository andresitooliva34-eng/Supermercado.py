import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from logic.carrito import Carrito
from logic.cliente import Cliente
from logic.pago import crear_pago
from logic.producto import Producto
from logic.repositorio import RepositorioJSON
from logic.supermercado import Supermercado
from logic.venta import Venta

from gui.exportador_historial import (
    exportar_historial_pdf,
    exportar_historial_excel
)

ROLES = (
    "Administrador", "Gerente", "Supervisor", "Cajero",
    "Repositor", "Vendedor"
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

        # Carga de productos
        self.supermercado = Supermercado()
        self.supermercado.cargar_productos()

        # Creación del carrito
        self.carrito = Carrito()

        # Repositorios JSON
        self.repo_clientes = RepositorioJSON("clientes.json")
        self.repo_ventas = RepositorioJSON("ventas.json")
        self.repo_empleados = RepositorioJSON("empleados.json")
        self.repo_categorias = RepositorioJSON("categorias.json")
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
        # FILTROS
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

    def _empleados(self):
        empleados = self.repo_empleados.cargar()
        if not empleados:
            empleados = [{
                "id": 1, "nombre": "Administrador", "dni": "00000000",
                "rol": "Administrador", "usuario": "admin",
                "clave": "admin123", "activo": True
            }]
            self.repo_empleados.guardar(empleados)
        return empleados

    def _actualizar_menu_administracion(self):
        self.menu_administracion.delete(0, tk.END)
        if self.empleado_actual is None:
            self.menu_administracion.add_command(label="Iniciar sesion", command=self.iniciar_sesion)
            return
        self.menu_administracion.add_command(
            label=f"Sesion: {self.empleado_actual['nombre']} ({self.empleado_actual['rol']})",
            state="disabled"
        )
        self.menu_administracion.add_separator()
        self.menu_administracion.add_command(label="Cerrar sesion", command=self.cerrar_sesion)
        rol = self.empleado_actual.get("rol")
        if rol in ("Administrador", "Gerente", "Supervisor", "Repositor"):
            self.menu_administracion.add_separator()
            self.menu_administracion.add_command(label="ABM de Productos", command=self.gestionar_productos)
        if rol in ("Administrador", "Gerente", "Supervisor"):
            self.menu_administracion.add_command(label="ABM de Categorias", command=self.gestionar_categorias)
        if rol in ("Administrador", "Gerente"):
            self.menu_administracion.add_command(label="ABM de Empleados", command=self.gestionar_empleados)

    def iniciar_sesion(self):
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Inicio de sesion")
        dialogo.resizable(False, False)
        dialogo.transient(self.ventana)
        entradas = []
        for fila, etiqueta in enumerate(("Usuario", "Contrasena")):
            tk.Label(dialogo, text=f"{etiqueta}:").grid(row=fila, column=0, padx=12, pady=7, sticky="e")
            entrada = tk.Entry(dialogo, width=26, show="*" if fila == 1 else "")
            entrada.grid(row=fila, column=1, padx=12, pady=7)
            entradas.append(entrada)

        def validar():
            usuario, clave = (entrada.get().strip() for entrada in entradas)
            empleado = next((e for e in self._empleados()
                             if e.get("usuario") == usuario and e.get("clave") == clave
                             and e.get("activo", True)), None)
            if empleado is None:
                messagebox.showerror("Acceso", "Usuario o contrasena invalidos.", parent=dialogo)
                return
            self.empleado_actual = empleado
            self._actualizar_menu_administracion()
            self.actualizar_cliente()
            dialogo.destroy()

        tk.Button(dialogo, text="Ingresar", command=validar).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Label(dialogo, text="Acceso inicial: admin / admin123").grid(row=3, column=0, columnspan=2, pady=(0, 10))
        entradas[0].focus_set()
        dialogo.bind("<Return>", lambda _evento: validar())
        dialogo.grab_set()

    def cerrar_sesion(self):
        self.empleado_actual = None
        self._actualizar_menu_administracion()
        self.actualizar_cliente()

    def _lista_categorias(self):
        datos = self.repo_categorias.cargar()
        nombres = sorted({p.categoria for p in self.supermercado.productos} |
                         {d.get("nombre", "") for d in datos if d.get("nombre")})
        existentes = {d.get("nombre") for d in datos}
        siguiente = max((d.get("id", 0) for d in datos), default=0) + 1
        for nombre in nombres:
            if nombre and nombre not in existentes:
                datos.append({"id": siguiente, "nombre": nombre})
                siguiente += 1
        if datos:
            self.repo_categorias.guardar(datos)
        return [d["nombre"] for d in datos if d.get("nombre")]

    def gestionar_productos(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar productos y stock")
        ventana.geometry("760x430")
        columnas = ("id", "nombre", "categoria", "precio", "stock")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for clave, titulo, ancho in (
            ("id", "ID", 55), ("nombre", "Producto", 230),
            ("categoria", "Categoria", 150), ("precio", "Precio", 120),
            ("stock", "Stock", 80)
        ):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho)
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        def recargar():
            tabla.delete(*tabla.get_children())
            for producto in self.supermercado.productos:
                tabla.insert("", "end", iid=str(producto.id), values=(
                    producto.id, producto.nombre, producto.categoria,
                    f"${producto.precio:,.2f}", producto.stock
                ))

        def formulario(producto=None):
            dialogo = tk.Toplevel(ventana)
            dialogo.title("Nuevo producto" if producto is None else "Editar producto")
            categorias = self._lista_categorias()
            valores = ("", categorias[0] if categorias else "", "0", "0") if producto is None else (
                producto.nombre, producto.categoria, str(producto.precio), str(producto.stock)
            )
            controles = []
            for fila, (etiqueta, valor) in enumerate(zip(("Nombre", "Categoria", "Precio", "Stock"), valores)):
                tk.Label(dialogo, text=f"{etiqueta}:").grid(row=fila, column=0, padx=10, pady=6, sticky="e")
                if etiqueta == "Categoria":
                    control = ttk.Combobox(dialogo, values=categorias, state="readonly", width=27)
                    control.set(valor)
                else:
                    control = tk.Entry(dialogo, width=30)
                    control.insert(0, valor)
                control.grid(row=fila, column=1, padx=10, pady=6)
                controles.append(control)

            def guardar():
                nombre, categoria, precio_texto, stock_texto = (c.get().strip() for c in controles)
                try:
                    precio = float(precio_texto.replace(",", "."))
                    stock = int(stock_texto)
                    if not nombre or not categoria or precio < 0 or stock < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Producto", "Completá los campos con valores válidos.", parent=dialogo)
                    return
                if producto is None:
                    producto_nuevo = Producto(self.supermercado.siguiente_id(), nombre, categoria, precio, stock)
                    self.supermercado.agregar_producto(producto_nuevo)
                else:
                    producto.nombre, producto.categoria = nombre, categoria
                    producto.precio, producto.stock = precio, stock
                self.supermercado.guardar_productos()
                self.actualizar_categorias()
                self.mostrar_productos()
                recargar()
                dialogo.destroy()

            tk.Button(dialogo, text="Guardar", command=guardar).grid(row=4, column=0, columnspan=2, pady=10)

        def editar():
            seleccion = tabla.selection()
            if seleccion:
                formulario(self.supermercado.buscar_por_id(int(seleccion[0])))

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            if messagebox.askyesno("Productos", "Eliminar el producto seleccionado?", parent=ventana):
                self.supermercado.eliminar_producto(int(seleccion[0]))
                self.supermercado.guardar_productos()
                self.actualizar_categorias()
                self.mostrar_productos()
                recargar()

        botones = tk.Frame(ventana)
        botones.pack(pady=(0, 12))
        for texto, comando in (("Nuevo", formulario), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()

    def gestionar_categorias(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar categorias")
        ventana.geometry("420x360")
        datos = self.repo_categorias.cargar()
        self._lista_categorias()
        datos = self.repo_categorias.cargar()
        tabla = ttk.Treeview(ventana, columns=("id", "nombre"), show="headings")
        tabla.heading("id", text="ID")
        tabla.heading("nombre", text="Categoria")
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        def recargar():
            tabla.delete(*tabla.get_children())
            for item in datos:
                tabla.insert("", "end", iid=str(item["id"]), values=(item["id"], item["nombre"]))

        def editar(nueva=False):
            seleccion = tabla.selection()
            actual = None if nueva or not seleccion else next((d for d in datos if str(d["id"]) == seleccion[0]), None)
            nombre = simpledialog.askstring("Categoria", "Nombre:", initialvalue="" if actual is None else actual["nombre"], parent=ventana)
            if nombre is None:
                return
            nombre = nombre.strip()
            if not nombre or any(d["nombre"].casefold() == nombre.casefold() and d is not actual for d in datos):
                messagebox.showwarning("Categoria", "Ingresá un nombre nuevo y no vacío.", parent=ventana)
                return
            if actual is None:
                datos.append({"id": max((d["id"] for d in datos), default=0) + 1, "nombre": nombre})
            else:
                anterior = actual["nombre"]
                actual["nombre"] = nombre
                for producto in self.supermercado.productos:
                    if producto.categoria == anterior:
                        producto.categoria = nombre
                self.supermercado.guardar_productos()
            self.repo_categorias.guardar(datos)
            self.actualizar_categorias()
            self.mostrar_productos()
            recargar()

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            item = next(d for d in datos if str(d["id"]) == seleccion[0])
            if any(p.categoria == item["nombre"] for p in self.supermercado.productos):
                messagebox.showwarning("Categoria", "Hay productos que usan esta categoria.", parent=ventana)
                return
            datos.remove(item)
            self.repo_categorias.guardar(datos)
            self.actualizar_categorias()
            recargar()

        botones = tk.Frame(ventana)
        botones.pack(pady=8)
        for texto, comando in (("Nueva", lambda: editar(True)), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()

    def gestionar_empleados(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar empleados")
        ventana.geometry("780x420")
        columnas = ("id", "nombre", "dni", "rol", "usuario", "activo")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for clave, titulo, ancho in (
            ("id", "ID", 45), ("nombre", "Nombre", 160), ("dni", "DNI", 95),
            ("rol", "Rol", 125), ("usuario", "Usuario", 120), ("activo", "Activo", 70)
        ):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho)
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        def recargar():
            tabla.delete(*tabla.get_children())
            for empleado in self._empleados():
                tabla.insert("", "end", iid=str(empleado["id"]), values=(
                    empleado["id"], empleado.get("nombre", ""), empleado.get("dni", ""),
                    empleado.get("rol", ""), empleado.get("usuario", ""),
                    "Sí" if empleado.get("activo", True) else "No"
                ))

        def formulario(empleado=None):
            dialogo = tk.Toplevel(ventana)
            dialogo.title("Nuevo empleado" if empleado is None else "Editar empleado")
            valores = ("", "", ROLES[0], "", "") if empleado is None else (
                empleado.get("nombre", ""), empleado.get("dni", ""), empleado.get("rol", ROLES[0]),
                empleado.get("usuario", ""), empleado.get("clave", "")
            )
            controles = []
            for fila, (etiqueta, valor) in enumerate(zip(("Nombre", "DNI", "Rol", "Usuario", "Contrasena"), valores)):
                tk.Label(dialogo, text=f"{etiqueta}:").grid(row=fila, column=0, padx=10, pady=5, sticky="e")
                if etiqueta == "Rol":
                    control = ttk.Combobox(dialogo, values=ROLES, state="readonly", width=27)
                    control.set(valor)
                else:
                    control = tk.Entry(dialogo, width=30, show="*" if etiqueta == "Contrasena" else "")
                    control.insert(0, valor)
                control.grid(row=fila, column=1, padx=10, pady=5)
                controles.append(control)
            activo = tk.BooleanVar(value=True if empleado is None else empleado.get("activo", True))
            tk.Checkbutton(dialogo, text="Empleado activo", variable=activo).grid(row=5, column=0, columnspan=2)

            def guardar():
                nombre, dni, rol, usuario, clave = (c.get().strip() for c in controles)
                empleados = self._empleados()
                if not all((nombre, dni, rol, usuario, clave)):
                    messagebox.showwarning("Empleados", "Completá todos los campos.", parent=dialogo)
                    return
                if any(e.get("usuario") == usuario and e is not empleado for e in empleados):
                    messagebox.showwarning("Empleados", "Ese usuario ya está registrado.", parent=dialogo)
                    return
                registro = empleado
                if registro is None:
                    registro = {"id": max((e["id"] for e in empleados), default=0) + 1}
                    empleados.append(registro)
                registro.update({"nombre": nombre, "dni": dni, "rol": rol,
                                 "usuario": usuario, "clave": clave, "activo": activo.get()})
                self.repo_empleados.guardar(empleados)
                recargar()
                dialogo.destroy()

            tk.Button(dialogo, text="Guardar", command=guardar).grid(row=6, column=0, columnspan=2, pady=10)

        def editar():
            seleccion = tabla.selection()
            if seleccion:
                empleado = next(e for e in self._empleados() if str(e["id"]) == seleccion[0])
                formulario(empleado)

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            empleados = self._empleados()
            empleado = next(e for e in empleados if str(e["id"]) == seleccion[0])
            if empleado.get("id") == self.empleado_actual.get("id"):
                messagebox.showwarning("Empleados", "No podés eliminar tu propio usuario activo.", parent=ventana)
                return
            if messagebox.askyesno("Empleados", "Eliminar el empleado seleccionado?", parent=ventana):
                empleados.remove(empleado)
                self.repo_empleados.guardar(empleados)
                recargar()

        botones = tk.Frame(ventana)
        botones.pack(pady=8)
        for texto, comando in (("Nuevo", formulario), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()

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
            text="Caja y administración del supermercado",
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
    # CERRAR APLICACIÓN
    # ------------------------------------------------------

    def _al_cerrar(self):

        if messagebox.askyesno(
            "Salir",
            "¿Cerrar la aplicación?"
        ):

            self.ventana.destroy()

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
                d.get("dni", ""),
                d.get("telefono", "")
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
            "",
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

            self.cliente.nombre = (
                entradas[0].get().strip()
            )

            self.cliente.apellido = (
                entradas[1].get().strip()
            )

            self.cliente.dni = (
                entradas[2].get().strip()
            )

            self.cliente.telefono = entradas[3].get().strip()

            self.guardar_cliente()
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
            "Venta actual"
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

            datos_venta = venta.to_dict()
            datos_venta["empleado_id"] = self.empleado_actual["id"]
            datos_venta["empleado_nombre"] = self.empleado_actual["nombre"]

            # Guarda la venta
            datos.append(
                datos_venta
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

    # ------------------------------------------------------
    # HISTORIAL
    # ------------------------------------------------------

    def mostrar_historial(self):

        ventas = self.repo_ventas.cargar()

        v = tk.Toplevel(
            self.ventana
        )

        v.title(
            "Historial de ventas"
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
