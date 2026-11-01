import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from mysql.connector import Error, IntegrityError

from logic.cliente import Cliente
from logic.validaciones import dni_valido, limpiar_dni, telefono_valido
from gui.ventana_productos import VentanaProductos

ROLES = (
    "Administrador", "Gerente", "Supervisor", "Cajero",
    "Repositor", "Vendedor"
)


class AdministracionMixin:
    """Ventanas de administración e inicio de sesión."""

    def _empleados(self):
        return self.repo_empleados.listar_empleados()

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
            self.menu_administracion.add_command(
                label="ABM de Clientes", command=self.gestionar_clientes
            )
            self.menu_administracion.add_command(label="ABM de Empleados", command=self.gestionar_empleados)

    def iniciar_sesion(self):
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Inicio de sesion")

        # Cierra la aplicación si el usuario cierra el login sin autenticarse
        def _al_cerrar_login():
            dialogo.destroy()
            if self.empleado_actual is None:
                self.ventana.destroy()
        dialogo.protocol("WM_DELETE_WINDOW", _al_cerrar_login)
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
            try:
                empleado = self.repo_empleados.autenticar_empleado(usuario, clave)
            except (Error, FileNotFoundError, ValueError) as error:
                messagebox.showerror(
                    "Base de datos",
                    f"No se pudo iniciar sesión:\n{error}",
                    parent=dialogo
                )
                return
            if empleado is None:
                messagebox.showerror("Acceso", "Usuario o contrasena invalidos.", parent=dialogo)
                return
            self.empleado_actual = empleado
            self._actualizar_menu_administracion()
            self.actualizar_cliente()
            dialogo.protocol("WM_DELETE_WINDOW", dialogo.destroy)
            dialogo.destroy()


        tk.Label(
            dialogo,
            text=(
                "Cuenta de prueba\n"
                "Usuario: admin\n"
                "Contraseña: admin123\n"
                "No usar en producción."
            ),
            fg="#2E7D32",
            font=("Arial", 9, "bold"),
            justify="center",
            wraplength=260
        ).grid(row=2, column=0, columnspan=2, pady=(0, 8))

        tk.Button(dialogo, text="Ingresar", command=validar).grid(row=3, column=0, columnspan=2, pady=(0, 10))
        entradas[0].focus_set()
        dialogo.bind("<Return>", lambda _evento: validar())
        dialogo.grab_set()

    def cerrar_sesion(self):
        self.empleado_actual = None
        self._actualizar_menu_administracion()
        self.actualizar_cliente()

    def _lista_categorias(self):
        return [item["nombre"] for item in self.repo_categorias.listar_categorias()]

    def gestionar_productos(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar productos y stock")
        ventana.geometry("900x430")
        ventana.transient(self.ventana)
        columnas = ("id", "codigo", "nombre", "categoria", "precio", "stock")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for clave, titulo, ancho in (
            ("id", "ID", 55), ("codigo", "Código", 100),
            ("nombre", "Producto", 230),
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
                    producto.id, producto.codigo, producto.nombre, producto.categoria,
                    f"${producto.precio:,.2f}", producto.stock
                ))

        def formulario(producto=None):
            dialogo = tk.Toplevel(ventana)
            dialogo.title("Nuevo producto" if producto is None else "Editar producto")
            dialogo.transient(ventana)
            try:
                categorias = self._lista_categorias()
            except (Error, FileNotFoundError, ValueError) as error:
                messagebox.showerror(
                    "Productos", f"No se pudieron cargar las categorías:\n{error}",
                    parent=dialogo
                )
                dialogo.destroy()
                return
            valores = (
                "", "", categorias[0] if categorias else "", "0", "0"
            ) if producto is None else (
                producto.codigo, producto.nombre, producto.categoria,
                str(producto.precio), str(producto.stock)
            )
            controles = []
            for fila, (etiqueta, valor) in enumerate(zip(
                ("Código", "Nombre", "Categoria", "Precio", "Stock"), valores
            )):
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
                codigo, nombre, categoria, precio_texto, stock_texto = (
                    c.get().strip() for c in controles
                )
                try:
                    precio = float(precio_texto.replace(",", "."))
                    stock = int(stock_texto)
                    if not nombre or not categoria or precio < 0 or stock < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Producto", "Completá los campos con valores válidos.", parent=dialogo)
                    return
                try:
                    fila_categoria = next(
                        (
                            item for item in self.repo_categorias.listar_categorias()
                            if item["nombre"] == categoria
                        ),
                        None
                    )
                    if fila_categoria is None:
                        raise ValueError("La categoría seleccionada ya no existe.")
                    id_categoria = fila_categoria["id"]
                    if producto is None:
                        self.repo_productos.agregar_producto(
                            codigo, nombre, precio, stock, id_categoria
                        )
                    else:
                        self.repo_productos.actualizar_producto(
                            producto.id, codigo, nombre, precio, stock,
                            id_categoria
                        )
                    self._recargar_catalogo()
                    self.actualizar_categorias()
                    self.mostrar_productos()
                    recargar()
                    dialogo.destroy()
                except (Error, FileNotFoundError, ValueError) as error:
                    messagebox.showerror(
                        "Base de datos", f"No se pudo guardar el producto:\n{error}",
                        parent=dialogo
                    )

            tk.Button(dialogo, text="Guardar", command=guardar).grid(row=4, column=0, columnspan=2, pady=10)
            dialogo.after(10, dialogo.grab_set)
            dialogo.focus_set()

        def editar():
            seleccion = tabla.selection()
            if seleccion:
                formulario(self.supermercado.buscar_por_id(int(seleccion[0])))

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            if messagebox.askyesno("Productos", "Eliminar el producto seleccionado?", parent=ventana):
                try:
                    self.repo_productos.eliminar_producto(int(seleccion[0]))
                    self._recargar_catalogo()
                    self.actualizar_categorias()
                    self.mostrar_productos()
                    recargar()
                except (Error, FileNotFoundError, ValueError) as error:
                    messagebox.showerror(
                        "Productos", str(error), parent=ventana
                    )

        botones = tk.Frame(ventana)
        botones.pack(pady=(0, 12))
        for texto, comando in (("Nuevo", formulario), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()
        ventana.after(10, ventana.grab_set)
        ventana.focus_set()
        self.ventana.wait_window(ventana)

    def gestionar_categorias(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar categorias")
        ventana.geometry("420x360")
        ventana.grab_set()
        tabla = ttk.Treeview(ventana, columns=("id", "nombre"), show="headings")
        tabla.heading("id", text="ID")
        tabla.heading("nombre", text="Categoria")
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        def recargar():
            datos = self.repo_categorias.listar_categorias()
            tabla.delete(*tabla.get_children())
            for item in datos:
                tabla.insert("", "end", iid=str(item["id"]), values=(item["id"], item["nombre"]))

        def editar(nueva=False):
            seleccion = tabla.selection()
            actual = None
            if not nueva and seleccion:
                actual = {
                    "id": int(seleccion[0]),
                    "nombre": tabla.item(seleccion[0], "values")[1]
                }
            nombre = simpledialog.askstring("Categoria", "Nombre:", initialvalue="" if actual is None else actual["nombre"], parent=ventana)
            if nombre is None:
                return
            nombre = nombre.strip()
            datos = self.repo_categorias.listar_categorias()
            if not nombre or any(
                d["nombre"].casefold() == nombre.casefold()
                and (actual is None or d["id"] != actual["id"])
                for d in datos
            ):
                messagebox.showwarning("Categoria", "Ingresá un nombre nuevo y no vacío.", parent=ventana)
                return
            try:
                self.repo_categorias.guardar_categoria({
                    "id": actual["id"] if actual else None,
                    "nombre": nombre
                })
                self._recargar_catalogo()
                self.actualizar_categorias()
                self.mostrar_productos()
                recargar()
            except (Error, IntegrityError, FileNotFoundError) as error:
                messagebox.showerror(
                    "Categoria", f"No se pudo guardar la categoría:\n{error}",
                    parent=ventana
                )

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                return
            try:
                self.repo_categorias.eliminar_categoria(int(seleccion[0]))
                self.actualizar_categorias()
                recargar()
            except IntegrityError:
                messagebox.showwarning(
                    "Categoria", "Hay productos que usan esta categoria.",
                    parent=ventana
                )
            except (Error, FileNotFoundError) as error:
                messagebox.showerror(
                    "Categoria", f"No se pudo eliminar la categoría:\n{error}",
                    parent=ventana
                )

        botones = tk.Frame(ventana)
        botones.pack(pady=8)
        for texto, comando in (("Nueva", lambda: editar(True)), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()

    def gestionar_clientes(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar clientes")
        ventana.geometry("760x420")
        ventana.transient(self.ventana)

        columnas = ("id", "nombre", "dni", "telefono", "ventas")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for clave, titulo, ancho in (
            ("id", "ID", 55),
            ("nombre", "Nombre", 220),
            ("dni", "DNI", 130),
            ("telefono", "Teléfono", 150),
            ("ventas", "Compras", 90)
        ):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho)
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        clientes = []

        def recargar():
            try:
                clientes[:] = self.repo_clientes.listar_clientes()
            except (Error, FileNotFoundError) as error:
                messagebox.showerror(
                    "Clientes", f"No se pudieron cargar:\n{error}",
                    parent=ventana
                )
                return
            tabla.delete(*tabla.get_children())
            for cliente in clientes:
                tabla.insert(
                    "",
                    "end",
                    iid=str(cliente["id"]),
                    values=(
                        cliente["id"],
                        f"{cliente['nombre']} {cliente['apellido']}".strip(),
                        cliente["dni"],
                        cliente["telefono"],
                        cliente["cantidad_ventas"]
                    )
                )

        def formulario(cliente=None):
            dialogo = tk.Toplevel(ventana)
            dialogo.title(
                "Nuevo cliente" if cliente is None else "Editar cliente"
            )
            dialogo.transient(ventana)

            valores = (
                ("Nombre", ""),
                ("Apellido", ""),
                ("DNI (opcional)", ""),
                ("Teléfono (opcional)", "")
            ) if cliente is None else (
                ("Nombre", cliente["nombre"]),
                ("Apellido", cliente["apellido"]),
                ("DNI (opcional)", cliente["dni"]),
                ("Teléfono (opcional)", cliente["telefono"])
            )
            entradas = []
            for fila, (etiqueta, valor) in enumerate(valores):
                tk.Label(dialogo, text=f"{etiqueta}:").grid(
                    row=fila, column=0, padx=10, pady=6, sticky="e"
                )
                entrada = tk.Entry(dialogo, width=30)
                entrada.insert(0, valor)
                entrada.grid(row=fila, column=1, padx=10, pady=6)
                entradas.append(entrada)

            def guardar():
                nombre = entradas[0].get().strip()
                apellido = entradas[1].get().strip()
                dni = limpiar_dni(entradas[2].get())
                telefono = entradas[3].get().strip()
                if not nombre:
                    messagebox.showwarning(
                        "Clientes", "El nombre es obligatorio.",
                        parent=dialogo
                    )
                    return
                if not dni_valido(dni):
                    messagebox.showwarning(
                        "Clientes", "El DNI debe tener 7 u 8 números.",
                        parent=dialogo
                    )
                    entradas[2].focus_set()
                    return
                if not telefono_valido(telefono):
                    messagebox.showwarning(
                        "Clientes", "El teléfono contiene caracteres no permitidos.",
                        parent=dialogo
                    )
                    entradas[3].focus_set()
                    return

                registro = Cliente(
                    cliente["id"] if cliente else 0,
                    nombre,
                    apellido,
                    dni,
                    telefono
                )
                try:
                    self.repo_clientes.guardar_cliente(registro)
                except (Error, FileNotFoundError, ValueError) as error:
                    messagebox.showerror(
                        "Clientes", f"No se pudo guardar:\n{error}",
                        parent=dialogo
                    )
                    return
                recargar()
                dialogo.destroy()

            tk.Button(
                dialogo, text="Guardar", command=guardar
            ).grid(row=4, column=0, columnspan=2, pady=10)
            dialogo.after(10, dialogo.grab_set)
            dialogo.focus_set()

        def editar():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning(
                    "Clientes", "Seleccioná un cliente para editar.",
                    parent=ventana
                )
                return
            cliente = next(
                item for item in clientes
                if str(item["id"]) == seleccion[0]
            )
            formulario(cliente)

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning(
                    "Clientes", "Seleccioná un cliente para eliminar.",
                    parent=ventana
                )
                return
            if not messagebox.askyesno(
                "Eliminar cliente",
                "¿Eliminar el cliente? Las ventas históricas se conservarán "
                "sin cliente asociado.",
                parent=ventana
            ):
                return
            try:
                self.repo_clientes.eliminar_cliente(int(seleccion[0]))
            except (Error, FileNotFoundError) as error:
                messagebox.showerror(
                    "Clientes", f"No se pudo eliminar:\n{error}",
                    parent=ventana
                )
                return
            recargar()

        botones = tk.Frame(ventana)
        botones.pack(pady=8)
        for texto, comando in (
            ("Nuevo", formulario),
            ("Editar", editar),
            ("Eliminar", eliminar)
        ):
            tk.Button(botones, text=texto, command=comando).pack(
                side="left", padx=5
            )
        recargar()

    def gestionar_empleados(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Administrar empleados")
        ventana.geometry("780x420")
        ventana.grab_set()
        columnas = ("id", "nombre", "rol", "usuario", "activo")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for clave, titulo, ancho in (
            ("id", "ID", 45), ("nombre", "Nombre", 200),
            ("rol", "Rol", 125), ("usuario", "Usuario", 120), ("activo", "Activo", 70)
        ):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho)
        tabla.pack(padx=12, pady=12, fill="both", expand=True)

        def recargar():
            try:
                empleados = self._empleados()
            except (Error, FileNotFoundError) as error:
                messagebox.showerror(
                    "Empleados", f"No se pudieron cargar:\n{error}",
                    parent=ventana
                )
                return
            tabla.delete(*tabla.get_children())
            for empleado in empleados:
                tabla.insert("", "end", iid=str(empleado["id"]), values=(
                    empleado["id"], empleado.get("nombre", ""),
                    empleado.get("rol", ""), empleado.get("usuario", ""),
                    "Sí" if empleado.get("activo", True) else "No"
                ))

        def formulario(empleado=None):
            dialogo = tk.Toplevel(ventana)
            dialogo.title("Nuevo empleado" if empleado is None else "Editar empleado")
            dialogo.grab_set()
            valores = ("", ROLES[0], "", "") if empleado is None else (
                empleado.get("nombre", ""), empleado.get("rol", ROLES[0]),
                empleado.get("usuario", ""), ""
            )
            controles = []
            for fila, (etiqueta, valor) in enumerate(zip(
                ("Nombre", "Rol", "Usuario", "Contrasena"), valores
            )):
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
            tk.Checkbutton(dialogo, text="Empleado activo", variable=activo).grid(row=4, column=0, columnspan=2)

            if empleado is not None:
                tk.Label(
                    dialogo,
                    text="Dejá la contraseña vacía para conservar la actual."
                ).grid(row=6, column=0, columnspan=2, pady=(0, 6))

            def guardar():
                nombre, rol, usuario, clave = (
                    c.get().strip() for c in controles
                )
                try:
                    empleados = self._empleados()
                except Error as error:
                    messagebox.showerror(
                        "Empleados", f"No se pudieron consultar:\n{error}",
                        parent=dialogo
                    )
                    return
                if not all((nombre, rol, usuario)) or (empleado is None and not clave):
                    messagebox.showwarning(
                        "Empleados", "Completá los campos obligatorios.",
                        parent=dialogo
                    )
                    return
                id_editado = empleado["id"] if empleado else None
                if any(e.get("usuario") == usuario and e["id"] != id_editado for e in empleados):
                    messagebox.showwarning("Empleados", "Ese usuario ya está registrado.", parent=dialogo)
                    return
                registro = {
                    "id": id_editado,
                    "nombre": nombre,
                    "rol": rol,
                    "usuario": usuario,
                    "activo": activo.get()
                }
                try:
                    registro["id"] = self.repo_empleados.guardar_empleado(
                        registro, clave or None
                    )
                    if (
                        self.empleado_actual
                        and self.empleado_actual.get("id") == registro["id"]
                    ):
                        self.empleado_actual.update(registro)
                        self._actualizar_menu_administracion()
                        self.actualizar_cliente()
                    recargar()
                    dialogo.destroy()
                except (Error, FileNotFoundError, IntegrityError, ValueError) as error:
                    messagebox.showerror(
                        "Empleados", f"No se pudo guardar el empleado:\n{error}",
                        parent=dialogo
                    )

            tk.Button(dialogo, text="Guardar", command=guardar).grid(row=5, column=0, columnspan=2, pady=10)
            # Espera a que se cierre el formulario y le devuelve el bloqueo a la ventana del ABM
            dialogo.wait_window()
            if ventana.winfo_exists():
                ventana.grab_set()

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
            if self.empleado_actual and empleado.get("id") == self.empleado_actual.get("id"):
                messagebox.showwarning("Empleados", "No podés eliminar tu propio usuario activo.", parent=ventana)
                return
            if messagebox.askyesno("Empleados", "Eliminar el empleado seleccionado?", parent=ventana):
                try:
                    self.repo_empleados.eliminar_empleado(empleado["id"])
                    recargar()
                except (Error, FileNotFoundError) as error:
                    messagebox.showerror(
                        "Empleados", f"No se pudo eliminar:\n{error}",
                        parent=ventana
                    )

        botones = tk.Frame(ventana)
        botones.pack(pady=8)
        for texto, comando in (("Nuevo", formulario), ("Editar", editar), ("Eliminar", eliminar)):
            tk.Button(botones, text=texto, command=comando).pack(side="left", padx=5)
        recargar()

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

            "Saravia, Samuel Eric",

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
