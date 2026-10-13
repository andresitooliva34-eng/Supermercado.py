import tkinter as tk
from tkinter import messagebox, ttk

from mysql.connector import Error

from logic.repositorio_productos import RepositorioProductosMySQL


class VentanaProductos(tk.Toplevel):
    """
    Ventana secundaria para trabajar con la tabla producto de MySQL:
    - Arriba: formulario de ALTA.
    - Abajo: buscador + tabla de CONSULTA.
    """

    def __init__(self, padre):
        super().__init__(padre)

        self.title("Productos (MySQL)")
        self.geometry("760x540")
        self.configure(bg="#F1F8E9")

        # La ventana usa el repositorio; no escribe SQL ella misma
        self.repo = RepositorioProductosMySQL()

        # Guarda {nombre_de_categoria: id_categoria}
        self.categorias = {}

        self._crear_formulario()
        self._crear_busqueda_y_tabla()

        self._cargar_categorias()
        self.consultar()


    # ------------------------------------------------------
    # FORMULARIO DE ALTA (usa grid)
    # ------------------------------------------------------

    def _crear_formulario(self):
        marco = tk.LabelFrame(
            self,
            text=" Nuevo producto ",
            bg="#F1F8E9",
            fg="#2E7D32",
            font=("Arial", 10, "bold")
        )
        marco.pack(fill="x", padx=15, pady=(15, 8))

        # grid: etiquetas y campos alineados en filas y columnas
        tk.Label(marco, text="Nombre:", bg="#F1F8E9").grid(
            row=0, column=0, padx=8, pady=6, sticky="e"
        )
        self.entrada_nombre = tk.Entry(marco, width=34)
        self.entrada_nombre.grid(row=0, column=1, columnspan=3,
                                 padx=8, pady=6, sticky="w")

        tk.Label(marco, text="Precio:", bg="#F1F8E9").grid(
            row=1, column=0, padx=8, pady=6, sticky="e"
        )
        self.entrada_precio = tk.Entry(marco, width=18)
        self.entrada_precio.grid(row=1, column=1, padx=8, pady=6)

        tk.Label(marco, text="Stock:", bg="#F1F8E9").grid(
            row=1, column=2, padx=8, pady=6, sticky="e"
        )
        self.entrada_stock = tk.Entry(marco, width=10)
        self.entrada_stock.grid(row=1, column=3, padx=8, pady=6, sticky="w")

        tk.Label(marco, text="Categoría:", bg="#F1F8E9").grid(
            row=2, column=0, padx=8, pady=6, sticky="e"
        )
        self.combo_categoria = ttk.Combobox(
            marco, state="readonly", width=16
        )
        self.combo_categoria.grid(row=2, column=1, padx=8, pady=6)

        tk.Button(
            marco,
            text="💾 Guardar producto",
            command=self.guardar,
            bg="#2E7D32",
            fg="white",
            font=("Arial", 9, "bold"),
            bd=0,
            cursor="hand2",
            padx=10,
            pady=4
        ).grid(row=2, column=3, padx=8, pady=6, sticky="w")


    # ------------------------------------------------------
    # BUSCADOR Y TABLA DE CONSULTA (usa pack)
    # ------------------------------------------------------

    def _crear_busqueda_y_tabla(self):
        # pack: apilamos buscador y tabla uno debajo del otro
        barra = tk.Frame(self, bg="#F1F8E9")
        barra.pack(fill="x", padx=15, pady=(8, 4))

        tk.Label(
            barra, text="🔎 Buscar por nombre o ID:", bg="#F1F8E9"
        ).pack(side="left")

        self.entrada_busqueda = tk.Entry(barra, width=28)
        self.entrada_busqueda.pack(side="left", padx=8)

        # Cada vez que se suelta una tecla, vuelve a consultar
        self.entrada_busqueda.bind(
            "<KeyRelease>", lambda _e: self.consultar()
        )

        columnas = ("id", "nombre", "categoria", "precio", "stock")

        self.tabla = ttk.Treeview(
            self, columns=columnas, show="headings", height=14
        )

        encabezados = (
            ("id", "ID", 55, "center"),
            ("nombre", "Producto", 280, "w"),
            ("categoria", "Categoría", 140, "w"),
            ("precio", "Precio", 110, "e"),
            ("stock", "Stock", 80, "center"),
        )

        for clave, texto, ancho, alineacion in encabezados:
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor=alineacion)

        self.tabla.pack(fill="both", expand=True, padx=15, pady=(4, 15))


    # ------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------

    def _cargar_categorias(self):
        # Llena el Combobox con las categorías que hay en la base
        try:
            filas = self.repo.listar_categorias()
        except (Error, FileNotFoundError) as error:
            messagebox.showerror(
                "Base de datos",
                f"No se pudieron cargar las categorías:\n{error}",
                parent=self
            )
            return

        self.categorias = {nombre: id_cat for id_cat, nombre in filas}
        self.combo_categoria["values"] = list(self.categorias.keys())

        if self.categorias:
            self.combo_categoria.current(0)


    def consultar(self):
        # CONSULTA: actualiza la tabla con lo que devuelve MySQL
        texto = self.entrada_busqueda.get().strip()

        try:
            filas = self.repo.listar_productos(texto)
        except (Error, FileNotFoundError) as error:
            messagebox.showerror(
                "Base de datos",
                f"No se pudo consultar:\n{error}",
                parent=self
            )
            return

        self.tabla.delete(*self.tabla.get_children())

        for id_p, nombre, categoria, precio, stock in filas:
            self.tabla.insert(
                "",
                "end",
                values=(
                    id_p, nombre, categoria,
                    f"${precio:,.2f}", stock
                )
            )


    def guardar(self):
        # ALTA: lee el formulario, valida y guarda en MySQL
        try:
            precio = float(self.entrada_precio.get().replace(",", "."))
            stock = int(self.entrada_stock.get())

        except ValueError:
            messagebox.showwarning(
                "Datos inválidos",
                "Precio y stock tienen que ser números.\n"
                "El stock debe ser entero.",
                parent=self
            )
            return

        nombre_categoria = self.combo_categoria.get()

        if nombre_categoria not in self.categorias:
            messagebox.showwarning(
                "Datos inválidos",
                "Elegí una categoría.",
                parent=self
            )
            return

        try:
            self.repo.agregar_producto(
                self.entrada_nombre.get(),
                precio,
                stock,
                self.categorias[nombre_categoria]
            )

        except ValueError as error:
            # Error de validación o regla de la base
            messagebox.showwarning("Atención", str(error), parent=self)
            return

        except Error as error:
            messagebox.showerror(
                "Base de datos",
                f"No se pudo guardar:\n{error}",
                parent=self
            )
            return

        messagebox.showinfo(
            "Listo", "Producto guardado correctamente.", parent=self
        )

        # Limpia el formulario y refresca la tabla
        for entrada in (
            self.entrada_nombre, self.entrada_precio, self.entrada_stock
        ):
            entrada.delete(0, tk.END)

        self.consultar()
