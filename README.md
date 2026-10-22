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
-  ABM de productos, categorías, clientes y empleados.
-  Ventana "Productos (MySQL)": alta y consulta de productos en la base de datos MySQL.

##  Roles y permisos

| Rol | Caja y ventas | Productos | Categorías | Clientes | Empleados |
|---|:---:|:---:|:---:|:---:|:---:|
| Administrador | ✅ | ✅ | ✅ | ✅ | ✅ |
| Gerente | ✅ | ✅ | ✅ | ✅ | ✅ |
| Supervisor | ✅ | ✅ | ✅ | — | — |
| Repositor | ✅ | ✅ | — | — | — |
| Cajero | ✅ | — | — | — | — |
| Vendedor | ✅ | — | — | — | — |

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

La aplicación requiere MySQL Server 8.0.18 o superior encendido y configurado para iniciar. El paso 2 instala el conector y las dependencias.

## Base de datos MySQL

1. Tener instalado MySQL Server (por ejemplo, junto con MySQL Workbench).
2. Para una instalación nueva, ejecutar `data/schema.sql` una sola vez como usuario `root`, desde Workbench o con:

   ```bash
   mysql -u root -p < data/schema.sql
   ```

   **El script borra y vuelve a crear `codemarket` y reemplaza las cuentas MySQL `cm_admin` y `cm_cajero`; no lo ejecutes sobre datos o cuentas que quieras conservar.** MySQL generará contraseñas aleatorias para ambas cuentas; copiá la generada para `cm_admin` y guardala solo en la configuración local. La base nueva incluye una cuenta de prueba de la aplicación. Si ya tenés la estructura plural (`categorias`, `clientes`, `empleados`, `productos`, `ventas`, `detalle_venta`), ejecutá en cambio `data/migracion_mysql.sql`. Esa actualización conserva los datos, agrega las columnas que falten y puede volver a ejecutarse.

   ```bash
   mysql -u root -p < data/migracion_mysql.sql
   ```
3. Copiar `data/config_db.example.json` como `data/config_db.json` y reemplazar `CONFIGURAR_LOCALMENTE` con la contraseña local de `cm_admin` que generó MySQL. No compartas ni subas `data/config_db.json`; el archivo local está ignorado por Git. También podés configurar la conexión con las variables `SUPERMERCADO_DB_HOST`, `SUPERMERCADO_DB_PORT`, `SUPERMERCADO_DB_USER`, `SUPERMERCADO_DB_PASSWORD` y `SUPERMERCADO_DB_NAME`.
4. Importar los datos JSON existentes sin borrar los archivos de respaldo:

   ```bash
   python -m logic.migrar_json_mysql
   ```

   La migración valida todos los archivos de origen antes de empezar, registra los IDs y se puede volver a ejecutar sin duplicar registros ya mapeados. Si un producto coincide por nombre, precio y categoría, se reutiliza sin cambiar el stock; los demás se agregan con un código `LEG-<id>`. Las ventas históricas se importan con sus detalles y sin volver a descontar inventario. Las contraseñas JSON se guardan como hashes bcrypt en MySQL; un usuario existente no se sobrescribe. Empleados incompletos se informan y se omiten. Si ocurre un error SQL durante la importación, corregilo y volvé a ejecutar la migración para continuar.
5. Para una base recién creada, iniciá sesión con las credenciales de prueba visibles en la ventana: **admin / admin123**. Si ya tenés una base CodeMarket existente y querés habilitar esa cuenta demo sin borrar tus datos, ejecutá una vez:

   ```bash
   mysql -u root -p < data/demo_admin.sql
   ```

   **Es una cuenta pública de demostración, no una contraseña segura.** Cambiala o desactivala antes de usar datos reales o exponer el servidor. Para crear una cuenta administrativa propia en vez de usar la demo, podés ejecutar `python -m logic.configurar_administrador` (si aún no hay una cuenta activa de Administrador/Gerente).
6. Iniciar con `python main.py`.

Los productos, categorías, clientes, empleados, ventas y detalles de venta se leen y escriben en MySQL. Los JSON solo son fuentes para la migración; la aplicación no los sincroniza durante el uso normal. Conservá las copias de respaldo de forma privada y protegida, ya que pueden contener datos personales.

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

## Pruebas

Para ejecutar las pruebas unitarias de configuración, migración y validaciones:

```bash
python -m unittest discover -s tests -v
```

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
│   ├── repositorio.py           → utilidades JSON legadas
│   ├── repositorio_mysql.py     → clientes, empleados, categorías y ventas
│   ├── migrar_json_mysql.py     → importación validada a MySQL
│   ├── configurar_administrador.py → creación segura del primer administrador
│   ├── repositorio_productos.py → consultas SQL del catálogo MySQL
│   ├── validaciones.py          → validación de DNI y teléfono
│   └── exportador_pdf.py        → factura del carrito en PDF (todavía no se usa en la venta)
├── data/                        → datos
│   ├── *.json                   → archivos históricos de origen/respaldo
│   ├── schema.sql               → crea la base MySQL codemarket
│   ├── demo_admin.sql           → habilita la cuenta demo en una base existente
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
