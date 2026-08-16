import tkinter as tk
from tkinter import messagebox, ttk

from logic.carrito import Carrito
from logic.cliente import Cliente
from logic.pago import crear_pago
from logic.repositorio import RepositorioJSON
from logic.supermercado import Supermercado
from logic.venta import Venta


class VentanaSupermercado:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Supermercado | Gestión de compras")
        ventana.geometry("920x590")
        ventana.configure(bg="#F1F8E9")
        self.supermercado = Supermercado(); self.supermercado.cargar_productos()
        self.carrito = Carrito()
        self.repo_clientes, self.repo_ventas = RepositorioJSON("clientes.json"), RepositorioJSON("ventas.json")
        self.cliente = self.cargar_cliente()

        tk.Label(ventana, text="SUPERMERCADO", font=("Arial", 20, "bold"), bg="#F1F8E9", fg="#2E7D32").pack(pady=(12, 4))
        self.etiqueta_cliente = tk.Label(ventana, bg="#F1F8E9"); self.etiqueta_cliente.pack()
        filtros = tk.Frame(ventana, bg="#F1F8E9"); filtros.pack(pady=9)
        tk.Label(filtros, text="🔎 Buscar por nombre:", bg="#F1F8E9").grid(row=0, column=0)
        self.entrada_busqueda = tk.Entry(filtros, width=26); self.entrada_busqueda.grid(row=0, column=1, padx=(5, 18))
        self.entrada_busqueda.bind("<KeyRelease>", lambda _e: self.filtrar_productos())
        tk.Label(filtros, text="📂 Categoría:", bg="#F1F8E9").grid(row=0, column=2)
        self.categoria = ttk.Combobox(filtros, state="readonly", width=17); self.categoria.grid(row=0, column=3, padx=5)
        self.categoria.bind("<<ComboboxSelected>>", lambda _e: self.filtrar_productos())
        tk.Button(filtros, text="Limpiar filtros", command=self.limpiar_filtros).grid(row=0, column=4, padx=8)

        columnas = ("id", "nombre", "categoria", "precio", "stock", "estado")
        self.tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=13)
        for clave, texto in zip(columnas, ("ID", "Producto", "Categoría", "Precio", "Stock", "Estado")): self.tabla.heading(clave, text=texto)
        for clave, ancho, alineacion in (("id",45,"center"),("nombre",240,"w"),("categoria",145,"w"),("precio",115,"e"),("stock",70,"center"),("estado",115,"center")): self.tabla.column(clave, width=ancho, anchor=alineacion)
        self.tabla.tag_configure("sin_stock", foreground="#B71C1C"); self.tabla.pack(padx=20, pady=4, fill="x")
        acciones = tk.Frame(ventana, bg="#F1F8E9"); acciones.pack(pady=10)
        tk.Label(acciones, text="Cantidad:", bg="#F1F8E9").pack(side="left")
        self.cantidad = tk.Spinbox(acciones, from_=1, to=100, width=5); self.cantidad.pack(side="left", padx=6)
        for texto, comando in (("Agregar al carrito",self.agregar_al_carrito),("Ver carrito",self.ver_carrito),("Finalizar compra",self.finalizar_compra),("Historial de compras",self.mostrar_historial),("Cambiar cliente",self.cambiar_cliente)):
            tk.Button(acciones, text=texto, command=comando, bg="#2E7D32" if texto == "Agregar al carrito" else None, fg="white" if texto == "Agregar al carrito" else None).pack(side="left", padx=4)
        self.estado = tk.Label(ventana, bg="#F1F8E9", font=("Arial",10,"bold")); self.estado.pack(pady=4)
        self.actualizar_cliente(); self.actualizar_categorias(); self.mostrar_productos(); self.actualizar_estado()

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
    def actualizar_estado(self): self.estado.config(text=f"Carrito: {self.carrito.cantidad_total()} productos  |  Total: ${self.carrito.calcular_total():,.2f}")

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
