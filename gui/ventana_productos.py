import tkinter as tk
from tkinter import messagebox, ttk

from mysql.connector import Error

from logic.repositorio_productos import RepositorioProductosMySQL


class VentanaProductos(tk.Toplevel):
    """Ventana para administrar productos almacenados en MySQL."""

    def __init__(self, padre):
        super().__init__(padre)

        self.title("Productos (MySQL)")
        self.geometry("850x600")
        self.minsize(780, 520)
        self.configure(bg="#F1F8E9")

        self.repo = RepositorioProductosMySQL()

        self.categorias = {}
        self.id_producto_seleccionado = None

        self._crear_formulario()
        self._crear_busqueda_y_tabla()
        self._cargar_categorias()
        self.consultar()

    def _crear_formulario(self):
        marco = tk.LabelFrame(
            self,
            text=" Datos del producto ",
            bg="#F1F8E9",
            fg="#2E7D32",
            font=("Arial", 10, "bold")
        )
        marco.pack(fill="x", padx=15, pady=(15, 8))

        tk.Label(marco, text="Nombre:", bg="#F1F8E9").grid(
            row=0, column=0, padx=8, pady=6, sticky="e"
        )
        self.entrada_nombre = tk.Entry(marco, width=34)
        self.entrada_nombre.grid(
            row=0, column=1, padx=8, pady=6, sticky="w"
        )
        tk.Label(marco, text="Código:", bg="#F1F8E9").grid(
            row=0, column=2, padx=8, pady=6, sticky="e"
        )
        self.entrada_codigo = tk.Entry(marco, width=18)
        self.entrada_codigo.grid(row=0, column=3, padx=8, pady=6)

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
            marco, state="readonly", width=18
        )
        self.combo_categoria.grid(row=2, column=1, padx=8, pady=6)

        botones = tk.Frame(marco, bg="#F1F8E9")
        botones.grid(row=2, column=2, columnspan=2, padx=8, pady=6, sticky="w")
        self._crear_boton(
            botones, "Guardar", self.guardar, "#2E7D32"
        ).pack(side="left", padx=(0, 5))
        self._crear_boton(
            botones, "Modificar", self.modificar, "#1565C0"
        ).pack(side="left", padx=5)
        self._crear_boton(
            botones, "Eliminar", self.eliminar, "#C62828"
        ).pack(side="left", padx=5)
        self._crear_boton(
            botones, "Limpiar", self.limpiar_formulario, "#616161"
        ).pack(side="left", padx=5)

    @staticmethod
    def _crear_boton(padre, texto, comando, color):
        return tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color,
            fg="white",
            font=("Arial", 9, "bold"),
            bd=0,
            cursor="hand2",
            padx=9,
            pady=4
        )

    def _crear_busqueda_y_tabla(self):
        barra = tk.Frame(self, bg="#F1F8E9")
        barra.pack(fill="x", padx=15, pady=(8, 4))

        tk.Label(
            barra, text="🔎 Buscar por nombre, categoría o ID:", bg="#F1F8E9"
        ).pack(side="left")

        self.entrada_busqueda = tk.Entry(barra, width=28)
        self.entrada_busqueda.pack(side="left", padx=8)
        self.entrada_busqueda.bind(
            "<KeyRelease>", lambda _evento: self.consultar()
        )
        self.entrada_busqueda.bind(
            "<Return>", lambda _evento: self.consultar()
        )
        self._crear_boton(
            barra, "Buscar", self.consultar, "#2E7D32"
        ).pack(side="left", padx=5)
        self._crear_boton(
            barra, "Ver todos", self.mostrar_todos, "#616161"
        ).pack(side="left", padx=5)

        columnas = ("id", "codigo", "nombre", "categoria", "precio", "stock")
        self.tabla = ttk.Treeview(
            self, columns=columnas, show="headings", height=14
        )
        encabezados = (
            ("id", "ID", 55, "center"),
            ("codigo", "Código", 95, "center"),
            ("nombre", "Producto", 220, "w"),
            ("categoria", "Categoría", 130, "w"),
            ("precio", "Precio", 100, "e"),
            ("stock", "Stock", 70, "center"),
        )
        for clave, texto, ancho, alineacion in encabezados:
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor=alineacion)

        self.tabla.pack(fill="both", expand=True, padx=15, pady=(4, 15))
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar)

    def _cargar_categorias(self):
        try:
            filas = self.repo.listar_categorias()
        except (Error, FileNotFoundError) as error:
            messagebox.showerror(
                "Base de datos",
                f"No se pudieron cargar las categorías:\n{error}",
                parent=self
            )
            return

        self.categorias = {nombre: id_categoria for id_categoria, nombre in filas}
        self.combo_categoria["values"] = list(self.categorias.keys())
        if self.categorias:
            self.combo_categoria.current(0)

    def consultar(self):
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
        for id_producto, codigo, nombre, categoria, precio, stock in filas:
            self.tabla.insert(
                "",
                "end",
                values=(
                    id_producto,
                    codigo,
                    nombre,
                    categoria,
                    f"${float(precio):,.2f}",
                    stock
                )
            )

    def _obtener_datos_formulario(self):
        try:
            precio = float(self.entrada_precio.get().replace(",", "."))
            stock = int(self.entrada_stock.get())
        except ValueError:
            messagebox.showwarning(
                "Datos inválidos",
                "Precio y stock tienen que ser números; el stock debe ser entero.",
                parent=self
            )
            return None

        nombre_categoria = self.combo_categoria.get()
        if nombre_categoria not in self.categorias:
            messagebox.showwarning(
                "Datos inválidos", "Elegí una categoría.", parent=self
            )
            return None

        return (
            self.entrada_codigo.get(),
            self.entrada_nombre.get(),
            precio,
            stock,
            self.categorias[nombre_categoria]
        )

    def guardar(self):
        datos = self._obtener_datos_formulario()
        if datos is None:
            return

        try:
            self.repo.agregar_producto(*datos)
        except ValueError as error:
            messagebox.showwarning("Atención", str(error), parent=self)
            return
        except Error as error:
            messagebox.showerror(
                "Base de datos", f"No se pudo guardar:\n{error}", parent=self
            )
            return

        messagebox.showinfo(
            "Listo", "Producto guardado correctamente.", parent=self
        )
        self.limpiar_formulario()
        self.consultar()

    def al_seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        valores = self.tabla.item(seleccion[0], "values")
        self.id_producto_seleccionado = int(valores[0])

        for entrada, valor in (
            (self.entrada_codigo, valores[1]),
            (self.entrada_nombre, valores[2]),
            (self.entrada_precio, str(valores[4]).replace("$", "").replace(",", "")),
            (self.entrada_stock, valores[5])
        ):
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)

        if valores[3] in self.categorias:
            self.combo_categoria.set(valores[3])

    def modificar(self):
        if self.id_producto_seleccionado is None:
            messagebox.showwarning(
                "Atención", "Seleccioná un producto de la tabla.", parent=self
            )
            return

        datos = self._obtener_datos_formulario()
        if datos is None:
            return

        try:
            self.repo.actualizar_producto(
                self.id_producto_seleccionado, *datos
            )
        except ValueError as error:
            messagebox.showwarning("Atención", str(error), parent=self)
            return
        except Error as error:
            messagebox.showerror(
                "Base de datos", f"No se pudo modificar:\n{error}", parent=self
            )
            return

        messagebox.showinfo(
            "Listo", "Producto modificado correctamente.", parent=self
        )
        self.limpiar_formulario()
        self.consultar()

    def eliminar(self):
        if self.id_producto_seleccionado is None:
            messagebox.showwarning(
                "Atención", "Seleccioná un producto de la tabla.", parent=self
            )
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Seguro que querés eliminar el producto seleccionado?",
            parent=self
        ):
            return

        try:
            self.repo.eliminar_producto(self.id_producto_seleccionado)
        except ValueError as error:
            messagebox.showwarning("No se puede eliminar", str(error), parent=self)
            return
        except Error as error:
            messagebox.showerror(
                "Base de datos", f"No se pudo eliminar:\n{error}", parent=self
            )
            return

        messagebox.showinfo("Listo", "Producto eliminado.", parent=self)
        self.limpiar_formulario()
        self.consultar()

    def limpiar_formulario(self):
        self.id_producto_seleccionado = None
        for entrada in (
            self.entrada_codigo,
            self.entrada_nombre,
            self.entrada_precio,
            self.entrada_stock
        ):
            entrada.delete(0, tk.END)
        self.tabla.selection_remove(self.tabla.selection())

    def mostrar_todos(self):
        self.entrada_busqueda.delete(0, tk.END)
        self.consultar()
