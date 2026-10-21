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

La aplicación requiere MySQL encendido y configurado para iniciar. El paso 2 instala el conector y las dependencias.

## Base de datos MySQL

1. Tener instalado MySQL Server (por ejemplo, junto con MySQL Workbench).
2. Para una instalación nueva, ejecutar `data/schema.sql` una sola vez como usuario `root`, desde Workbench o con:

   ```bash
   mysql -u root -p < data/schema.sql
   ```

   **El script borra y vuelve a crear `codemarket`; no lo ejecutes sobre una base que quieras conservar.** Si ya tenés la estructura plural (`categorias`, `clientes`, `empleados`, `productos`, `ventas`, `detalle_venta`), ejecutá en cambio `data/migracion_mysql.sql` una sola vez. Esa actualización agrega la contraseña/estado del empleado y permite clientes sin DNI ni limitar los roles de la app.

   ```bash
   mysql -u root -p < data/migracion_mysql.sql
   ```
3. Copiar `data/config_db.example.json` como `data/config_db.json` y reemplazar el marcador de contraseña por la credencial local de MySQL para ese usuario. No compartas ni subas `data/config_db.json`; el archivo local está ignorado por Git. La contraseña de ejemplo no es una credencial válida.
4. Importar los datos JSON existentes sin borrar los archivos de respaldo:

   ```bash
   python -m logic.migrar_json_mysql
   ```

   La migración es repetible y registra los IDs de origen para evitar reimportar registros. Si un producto coincide por nombre, precio y categoría, se reutiliza sin cambiar el stock; los demás se agregan con un código `LEG-<id>`. Las ventas históricas se importan con sus detalles y sin volver a descontar inventario. Las ventas JSON sin empleado asociado se asignan al empleado administrador importado; empleados JSON incompletos se informan y se omiten.
5. Iniciar con `python main.py`. En una base nueva, usar `groldan / Admin123`; en una base migrada, usar un empleado importado que tenga contraseña.

Los productos, categorías, clientes, empleados, ventas y detalles de venta se leen y escriben en MySQL. Los archivos JSON permanecen como respaldo y no se sincronizan durante el uso normal.

##  Tecnologías utilizadas

- Python y Tkinter (interfaz)
- MySQL con `mysql-connector-python` (base de datos)
- ReportLab (exportación a PDF)
- OpenPyXL (exportación a Excel)
- Git y GitHub

## 🗃️ CRUD de productos en MySQL

Desde **Archivo → Productos (MySQL)** se abre una ventana que permite
guardar, buscar, modificar y eliminar productos. Al seleccionar una fila,
sus datos se cargan en el formulario para poder editarla.

Las operaciones SQL están separadas de la interfaz en
`logic/repositorio_productos.py` y usan las tablas `productos` y `categorias`
del esquema definido. El repositorio consulta el código real del producto.
La configuración de conexión se lee desde
`data/config_db.json`; para prepararla, copiá
`data/config_db.example.json` a ese nombre y completá los datos locales de MySQL.

El CRUD utiliza explícitamente las columnas documentadas en `data/schema.sql`.
No se detectan nombres de tablas alternativos ni se adivinan columnas.

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
│   ├── supermercado.py          → modelo en memoria del catálogo
│   ├── repositorio.py           → acceso legado a JSON (respaldo/migración)
│   ├── repositorio_mysql.py     → clientes, empleados, categorías y ventas
│   ├── migrar_json_mysql.py     → importación idempotente de datos existentes
│   ├── repositorio_productos.py → consultas SQL del catálogo MySQL
│   ├── validaciones.py          → validación de DNI y teléfono
│   └── exportador_pdf.py        → factura del carrito en PDF (todavía no se usa en la venta)
├── data/                        → datos
│   ├── *.json                   → archivos históricos de origen/respaldo
│   ├── schema.sql               → crea la base MySQL codemarket
│   ├── migracion_mysql.sql      → actualiza una base existente sin borrarla
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
