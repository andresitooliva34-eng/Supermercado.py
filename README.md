# 🛒 Supermercado — Sistema de Gestión

Aplicación de escritorio para la caja y la administración de un supermercado, hecha en Python con Tkinter. Proyecto académico grupal.

## ¿Qué es?

Es un programa para usar en la computadora de un supermercado. Con él, el cajero arma la compra de un cliente, la cobra en efectivo, con tarjeta o con Mercado Pago, y el sistema descuenta del stock lo que se vendió. Cada venta queda guardada en un historial que se puede exportar a PDF o a Excel.

Cada empleado entra con su usuario y su contraseña, y ve solo las opciones de su rol: un cajero vende; un repositor, además, carga productos; un gerente o un administrador también puede dar de alta empleados.

##  Funcionalidades

-  Inicio de sesión de empleados, obligatorio para usar la app.
-  Roles y permisos (ver la tabla de abajo).
-  Catálogo de productos con búsqueda por nombre, filtro por categoría y opción "Solo con stock".
-  Carrito de compras: agregar productos con su cantidad, modificar, eliminar y vaciar.
-  Cobro en efectivo, con tarjeta o con Mercado Pago.
-  Control de stock: si falta stock de algún producto, la venta no se confirma y no se descuenta nada.
-  Datos del cliente, con validación de DNI y teléfono.
-  Historial de ventas, exportable a PDF y a Excel.
-  ABM de productos,  de categorías y de empleados.
-  Ventana "Productos (MySQL)": alta y consulta de productos en la base de datos MySQL.

##  Roles y permisos

| Rol | Caja y ventas | Productos | Categorías | Empleados |
|---|:---:|:---:|:---:|:---:|
| Administrador | ✅ | ✅ | ✅ | ✅ |
| Gerente | ✅ | ✅ | ✅ | ✅ |
| Supervisor | ✅ | ✅ | ✅ | — |
| Repositor | ✅ | ✅ | — | — |
| Cajero | ✅ | — | — | — |
| Vendedor | ✅ | — | — | — |

##  Cómo ejecutarlo

Se necesita Python 3.10 o superior. Tkinter ya viene incluido con Python en Windows.

1. Descargar el proyecto: botón **Code → Download ZIP** en GitHub, o con Git:

   ```bash
   git clone https://github.com/andresitooliva34-eng/Supermercado.py.git
   cd Supermercado.py
   ```

2. Instalar los paquetes que usa la app:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Abrir la aplicación:

   ```bash
   python main.py
   ```

La app necesita el paquete `mysql-connector-python` para abrir, aunque no se use la base de datos. El paso 2 lo instala.

##  Acceso inicial

- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Rol:** Administrador

Si `data/empleados.json` está vacío, la app crea este usuario sola. Después, los empleados se gestionan desde **Administración → ABM de Empleados**.

## 🗄️ Base de datos MySQL (opcional)

Solo hace falta para usar la ventana **Archivo → Productos (MySQL)**.

1. Tener instalado MySQL Server (por ejemplo, junto con MySQL Workbench).
2. Ejecutar `data/schema.sql` una sola vez como usuario `root`, desde Workbench o con:

   ```bash
   mysql -u root -p < data/schema.sql
   ```

   El script crea la base `codemarket` con sus tablas y datos de prueba, y dos usuarios de prueba: `cm_admin` y `cm_cajero`.

3. Copiar `data/config_db.example.json` con el nombre `data/config_db.json`. Ya trae los datos del usuario `cm_admin`. Ese archivo no se sube a GitHub porque está en `.gitignore`.
4. Abrir la app y entrar a **Archivo → Productos (MySQL)**.

##  Dónde se guardan los datos

| Datos | Dónde se guardan |
|---|---|
| Productos de la pantalla principal y del carrito | `data/productos.json` |
| Categorías | `data/categorias.json` |
| Clientes | `data/clientes.json` |
| Empleados | `data/empleados.json` |
| Ventas | `data/ventas.json` |
| Productos de la ventana "Productos (MySQL)" | Base MySQL `codemarket` |

El diseño completo de la base (categorías, productos, clientes, empleados, ventas y detalle de venta) está en `data/schema.sql`. Por ahora la app usa MySQL solo en la ventana de productos; el resto de los módulos sigue guardando en JSON.

##  Tecnologías utilizadas

- Python y Tkinter (interfaz)
- JSON (archivos de datos)
- MySQL con `mysql-connector-python` (base de datos)
- ReportLab (exportación a PDF)
- OpenPyXL (exportación a Excel)
- Git y GitHub

##  Estructura del proyecto

```text
Supermercado.py/
├── main.py                      → arranca la aplicación
├── requirements.txt             → paquetes que hay que instalar
├── gui/                         → ventanas (Tkinter)
│   ├── menu.py                  → ventana principal: login, caja, carrito, historial y ABM
│   ├── ventana_productos.py     → ventana "Productos (MySQL)"
│   └── exportador_historial.py  → exporta el historial a PDF y a Excel
├── logic/                       → reglas del negocio
│   ├── producto.py              → clase Producto y control de stock
│   ├── carrito.py               → clase Carrito: agregar, modificar, eliminar y vaciar
│   ├── venta.py                 → clase Venta
│   ├── pago.py                  → pagos: Efectivo, Tarjeta y Mercado Pago
│   ├── cliente.py               → clase Cliente
│   ├── supermercado.py          → catálogo de productos (productos.json)
│   ├── repositorio.py           → lectura y escritura de los archivos JSON
│   ├── repositorio_productos.py → consultas SQL de productos (MySQL)
│   ├── validaciones.py          → validación de DNI y teléfono
│   └── exportador_pdf.py        → factura del carrito en PDF (todavía no se usa en la venta)
├── data/                        → datos
│   ├── *.json                   → productos, categorías, clientes, empleados y ventas
│   ├── schema.sql               → crea la base MySQL codemarket
│   ├── conexion.py              → conexión a MySQL
│   └── config_db.example.json   → ejemplo de configuración de la base
└── assets/                      → íconos, imagen y estilos
```

## Integrantes

| Integrante | Usuario de GitHub |
|---|---|
| Lozano Bazán, Facundo Nicolás | [Facundolozano-7](https://github.com/Facundolozano-7) |
| Marín Silva, Rafael Alejandro | [rafaelmrn19](https://github.com/rafaelmrn19) |
| Oliva Ruiz, Roberto Andrés | [andresitooliva34-eng](https://github.com/andresitooliva34-eng) |
| Saravia, Samuel Eric | [saraviasamuel](https://github.com/saraviasamuel) |

##  Bitácora

El registro semana a semana de lo que hicimos está en [bitacora.md].
