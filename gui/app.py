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

from gui.exportador_historial import exportar_historial_pdf, exportar_historial_excel


def ruta_recurso(relativa):
    """Devuelve la ruta correcta a un recurso, tanto ejecutando con Python
    como empaquetado en un .exe con PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relativa)


class VentanaSupermercado:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Supermercado | Gestión de compras")
        ventana.iconbitmap(ruta_recurso("assets/supermercado_icon.ico"))
        ventana.geometry("920x590")       
        ventana.configure(bg="#F1F8E9")
        self.supermercado = Supermercado(); self.supermercado.cargar_productos()
        self.carrito = Carrito()
        self.repo_clientes, self.repo_ventas = RepositorioJSON("clientes.json"), RepositorioJSON("ventas.json")
        self.cliente = self.cargar_cliente()
        self._crear_menu_archivo()

        tk.Label(ventana, text="🛒 SUPERMERCADO 🛒", font=("Arial", 22, "bold"), bg="#F1F8E9", fg="#2E7D32").pack(pady=(14, 2))
        tk.Label(ventana, text="Tu changuito de compras, más fácil", font=("Arial", 10, "italic"), bg="#F1F8E9", fg="#558B2F").pack(pady=(0, 8))
        tk.Frame(ventana, bg="#A5D6A7", height=2).pack(fill="x", padx=60, pady=(0, 6))

        self.etiqueta_cliente = tk.Label(ventana, bg="#F1F8E9"); self.etiqueta_cliente.pack()
        filtros = tk.Frame(ventana, bg="#F1F8E9"); filtros.pack(pady=9)
        tk.Label(filtros, text="🔎 Buscar por nombre:", bg="#F1F8E9").grid(row=0, column=0)
        self.entrada_busqueda = tk.Entry(filtros, width=26); self.entrada_busqueda.grid(row=0, column=1, padx=(5, 18))
        self.entrada_busqueda.bind("<KeyRelease>", lambda _e: self.filtrar_productos())
        tk.Label(filtros, text="📂 Categoría:", bg="#F1F8E9").grid(row=0, column=2)
        self.categoria = ttk.Combobox(filtros, state="readonly", width=17); self.categoria.grid(row=0, column=3, padx=5)
        self.categoria.bind("<<ComboboxSelected>>", lambda _e: self.filtrar_productos())
        self._crear_boton_accion(filtros, "🧹 Limpiar filtros", self.limpiar_filtros).grid(row=0, column=4, padx=8)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview.Heading", background="#2E7D32", foreground="white", font=("Arial", 9, "bold"))
        estilo.map("Treeview.Heading", background=[("active", "#388E3C")])
        estilo.configure("Treeview", rowheight=24, font=("Arial", 9))

        columnas = ("id", "nombre", "categoria", "precio", "stock", "estado")
        self.tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=13)
        for clave, texto in zip(columnas, ("ID", "Producto", "Categoría", "Precio", "Stock", "Estado")): self.tabla.heading(clave, text=texto)
        for clave, ancho, alineacion in (("id",45,"center"),("nombre",240,"w"),("categoria",145,"w"),("precio",115,"e"),("stock",70,"center"),("estado",115,"center")): self.tabla.column(clave, width=ancho, anchor=alineacion)
        self.tabla.tag_configure("sin_stock", foreground="#B71C1C"); self.tabla.pack(padx=20, pady=4, fill="x")
        acciones = tk.Frame(ventana, bg="#F1F8E9"); acciones.pack(pady=10)
        tk.Label(acciones, text="Cantidad:", bg="#F1F8E9").pack(side="left")
        self.cantidad = tk.Spinbox(acciones, from_=1, to=100, width=5); self.cantidad.pack(side="left", padx=6)
        botones_info = (
            ("🛒 Agregar al carrito", self.agregar_al_carrito, True),
            ("👁 Ver carrito", self.ver_carrito, False),
            ("💳 Finalizar compra", self.finalizar_compra, False),
            ("📜 Historial", self.mostrar_historial, False),
            ("👤 Cambiar cliente", self.cambiar_cliente, False),
        )
        for texto, comando, destacado in botones_info:
            self._crear_boton_accion(acciones, texto, comando, destacado).pack(side="left", padx=4)
        self.estado = tk.Label(ventana, bg="#F1F8E9", font=("Arial",10,"bold"), fg="#2E7D32"); self.estado.pack(pady=4)
        self.actualizar_cliente(); self.actualizar_categorias(); self.mostrar_productos(); self.actualizar_estado()

    @staticmethod
    def _aplicar_hover(boton, color_normal, color_hover):
        boton.bind("<Enter>", lambda e: boton.config(bg=color_hover))
        boton.bind("<Leave>", lambda e: boton.config(bg=color_normal))

    def _crear_boton_accion(self, padre, texto, comando, destacado=False):
        color_normal = "#2E7D32" if destacado else "#558B2F"
        color_hover = "#388E3C" if destacado else "#689F38"
        boton = tk.Button(
            padre, text=texto, command=comando,
            bg=color_normal, fg="white", font=("Arial", 9, "bold"),
            bd=0, relief="flat", cursor="hand2", padx=10, pady=4
        )
        self._aplicar_hover(boton, color_normal, color_hover)
        return boton

    def _crear_menu_archivo(self):
        barra_menu = tk.Menu(self.ventana)
        self.ventana.config(menu=barra_menu)
        self.barra_menu = barra_menu

        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        menu_archivo.add_command(
            label="Exportar Historial a PDF",
            command=lambda: exportar_historial_pdf(self.ventana, self.repo_ventas.cargar())
        )
        menu_archivo.add_command(
            label="Exportar Historial a Excel",
            command=lambda: exportar_historial_excel(self.ventana, self.repo_ventas.cargar())
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.ventana.quit)

        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_acerca = tk.Menu(barra_menu, tearoff=0)
        menu_acerca.add_command(label="Acerca de Supermercado", command=self._mostrar_acerca_de)
        barra_menu.add_cascade(label="Acerca de", menu=menu_acerca)

    def _mostrar_acerca_de(self):
        ventana_acerca = tk.Toplevel(self.ventana)
        ventana_acerca.title("Acerca de Supermercado")
        ventana_acerca.geometry("420x460")
        ventana_acerca.configure(bg="#F1F8E9")
        ventana_acerca.resizable(False, False)
        ventana_acerca.grab_set()

        tk.Label(
            ventana_acerca, text="SUPERMERCADO", font=("Arial", 20, "bold"),
            bg="#F1F8E9", fg="#2E7D32"
        ).pack(pady=(25, 0))

        tk.Label(
            ventana_acerca, text="Sistema de Gestión de Compras",
            font=("Arial", 10, "italic"), bg="#F1F8E9", fg="#558B2F"
        ).pack(pady=(0, 15))

        tk.Frame(ventana_acerca, bg="#558B2F", height=1).pack(fill="x", padx=40, pady=(0, 15))

        tk.Label(
            ventana_acerca, text="Proyecto académico",
            font=("Arial", 10), bg="#F1F8E9", fg="#2E7D32"
        ).pack()
        tk.Label(
            ventana_acerca,
            text="Tecnicatura Superior en Desarrollo de Software\nInstituto Superior Politécnico Córdoba (ISPC)",
            font=("Arial", 9, "italic"), bg="#F1F8E9", fg="#558B2F", justify="center"
        ).pack(pady=(2, 15))

        tk.Label(
            ventana_acerca, text="Integrantes:",
            font=("Arial", 11, "bold"), bg="#F1F8E9", fg="#2E7D32"
        ).pack(pady=(0, 8))

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
                ventana_acerca, text=f"•  {nombre}",
                font=("Arial", 10), bg="#F1F8E9", fg="#33691E", anchor="w"
            ).pack(fill="x", padx=55, pady=1)

        tk.Button(
            ventana_acerca, text="Cerrar", command=ventana_acerca.destroy,
            bg="#2E7D32", fg="white", font=("Arial", 10, "bold"),
            bd=0, relief="flat", cursor="hand2", width=12
        ).pack(pady=20)

    def cargar_cliente(self):
        datos = self.repo_clientes.cargar()
        if datos:
            d = datos[0]; cliente = Cliente(d["id"], d["nombre"], d.get("apellido", ""), d.get("email", "")); cliente.historial_compras = d.get("historial_compras", []); return cliente
        cliente = Cliente(1, "Cliente", "General", ""); self.repo_clientes.guardar([cliente.to_dict()]); return cliente

    def guardar_cliente(self): self.repo_clientes.guardar([self.cliente.to_dict()])
    def actualizar_cliente(self): self.etiqueta_cliente.config(text=f"Cliente activo: {self.cliente.nombre_completo}")

    def cambiar_cliente(self):
        v = tk.Toplevel(self.ventana); v.title("Datos del cliente"); v.resizable(False, False); entradas = []
        for fila, (texto, valor) in enumerate((("Nombre",self.cliente.nombre),("Apellido",self.cliente.apellido),("Email",self.cliente.email))):
            tk.Label(v, text=f"{texto}:").grid(row=fila,column=0,padx=10,pady=6,sticky="e"); e=tk.Entry(v,width=30); e.insert(0,valor); e.grid(row=fila,column=1,padx=10,pady=6); entradas.append(e)
        def guardar():
            if not entradas[0].get().strip(): messagebox.showwarning("Cliente","El nombre es obligatorio.",parent=v); return
            self.cliente.nombre, self.cliente.apellido, self.cliente.email = (e.get().strip() for e in entradas); self.guardar_cliente(); self.actualizar_cliente(); v.destroy()
        tk.Button(v,text="Guardar",command=guardar).grid(row=3,column=0,columnspan=2,pady=10)

    def actualizar_categorias(self):
        self.categoria["values"] = ["Todas"] + sorted({p.categoria for p in self.supermercado.productos}); self.categoria.set("Todas")

    def mostrar_productos(self, productos=None):
        self.tabla.delete(*self.tabla.get_children())
        for p in self.supermercado.productos if productos is None else productos:
            estado = "Disponible" if p.stock > 0 else "SIN STOCK"; self.tabla.insert("","end",values=(p.id,p.nombre,p.categoria,f"${p.precio:,.2f}",p.stock,estado),tags=("sin_stock",) if p.stock == 0 else ())

    def filtrar_productos(self):
        texto, categoria = self.entrada_busqueda.get().strip().lower(), self.categoria.get()
        self.mostrar_productos([p for p in self.supermercado.productos if texto in p.nombre.lower() and (categoria == "Todas" or p.categoria == categoria)])
    def limpiar_filtros(self): self.entrada_busqueda.delete(0,tk.END); self.categoria.set("Todas"); self.mostrar_productos()

    def agregar_al_carrito(self):
        sel = self.tabla.selection()
        if not sel: messagebox.showwarning("Atención","Seleccioná un producto de la tabla."); return
        p = self.supermercado.buscar_por_id(int(self.tabla.item(sel[0])["values"][0]))
        if self.carrito.agregar_producto(p,int(self.cantidad.get())): self.actualizar_estado(); messagebox.showinfo("Carrito","Producto agregado al carrito.")
        else: messagebox.showwarning("Stock","No hay suficiente stock disponible.")
    def actualizar_estado(self): self.estado.config(text=f"🛒 Carrito: {self.carrito.cantidad_total()} productos  |  Total: ${self.carrito.calcular_total():,.2f}")

    def ver_carrito(self):
        v=tk.Toplevel(self.ventana); v.title("Mi carrito"); v.geometry("610x400"); tabla=ttk.Treeview(v,columns=("producto","cantidad","subtotal"),show="headings",height=11)
        for k,t in (("producto","Producto"),("cantidad","Cant."),("subtotal","Subtotal")): tabla.heading(k,text=t)
        tabla.column("producto",width=300); tabla.column("cantidad",width=100,anchor="center"); tabla.column("subtotal",width=150,anchor="e"); tabla.pack(padx=15,pady=15,fill="x")
        total=tk.Label(v,font=("Arial",12,"bold")); total.pack(pady=3)
        def recargar():
            tabla.delete(*tabla.get_children())
            for i in self.carrito.items: tabla.insert("","end",iid=str(i["producto"].id),values=(i["producto"].nombre,i["cantidad"],f"${i['producto'].precio*i['cantidad']:,.2f}"))
            total.config(text=f"TOTAL: ${self.carrito.calcular_total():,.2f}"); self.actualizar_estado()
        def eliminar():
            if tabla.selection(): self.carrito.eliminar_producto(int(tabla.selection()[0])); recargar()
        def modificar():
            if not tabla.selection(): return
            if not self.carrito.modificar_cantidad(int(tabla.selection()[0]),int(spin.get())): messagebox.showwarning("Stock","Cantidad no disponible.",parent=v)
            recargar()
        pie=tk.Frame(v); pie.pack(pady=8); tk.Label(pie,text="Cantidad:").pack(side="left"); spin=tk.Spinbox(pie,from_=1,to=100,width=5); spin.pack(side="left",padx=4)
        tk.Button(pie,text="Modificar",command=modificar).pack(side="left",padx=4); tk.Button(pie,text="Eliminar",command=eliminar).pack(side="left",padx=4); tk.Button(pie,text="Vaciar carrito",command=lambda:(self.carrito.vaciar(),recargar())).pack(side="left",padx=4); recargar()

    def finalizar_compra(self):
        if not self.carrito.items: messagebox.showwarning("Carrito","El carrito está vacío."); return
        d=tk.Toplevel(self.ventana); d.title("Finalizar compra"); d.resizable(False,False); tk.Label(d,text=f"Total a pagar: ${self.carrito.calcular_total():,.2f}",font=("Arial",12,"bold")).pack(padx=35,pady=(15,8)); metodo=tk.StringVar(value="Efectivo")
        for opcion in ("Efectivo","Tarjeta","Mercado Pago"): tk.Radiobutton(d,text=opcion,variable=metodo,value=opcion).pack(anchor="w",padx=35)
        def confirmar():
            for item in self.carrito.items:
                if not item["producto"].reducir_stock(item["cantidad"]): messagebox.showerror("Stock","El stock cambió. Revisá el carrito.",parent=d); return
            datos=self.repo_ventas.cargar(); venta=Venta(max((x["id"] for x in datos),default=0)+1,self.cliente,self.carrito,metodo.get())
            datos.append(venta.to_dict()); self.repo_ventas.guardar(datos); self.cliente.agregar_compra(venta.id); self.guardar_cliente(); self.supermercado.guardar_productos(); self.carrito.vaciar(); self.actualizar_estado(); self.mostrar_productos(); d.destroy(); messagebox.showinfo("Compra realizada",f"Venta #{venta.id:03d} registrada.\n{crear_pago(venta.metodo_pago).pagar(venta.total)}")
        tk.Button(d,text="Confirmar pago",command=confirmar,bg="#2E7D32",fg="white").pack(pady=15)

    def mostrar_historial(self):
        ventas=self.repo_ventas.cargar(); v=tk.Toplevel(self.ventana); v.title("Historial de compras"); v.geometry("590x330"); tabla=ttk.Treeview(v,columns=("id","cliente","total","fecha","pago"),show="headings",height=12)
        for k,t in (("id","Venta"),("cliente","Cliente"),("total","Total"),("fecha","Fecha"),("pago","Pago")): tabla.heading(k,text=t)
        tabla.pack(padx=12,pady=12,fill="both",expand=True)
        for x in reversed(ventas): tabla.insert("","end",values=(f"#{x['id']:03d}",x.get("cliente_nombre",""),f"${x['total']:,.2f}",x["fecha"],x["metodo_pago"]))


def iniciar_interfaz():
    ventana=tk.Tk(); VentanaSupermercado(ventana); ventana.mainloop()