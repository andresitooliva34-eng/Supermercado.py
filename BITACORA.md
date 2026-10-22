# Bitácora de equipo — CodeMarket

**Proyecto:** CodeMarket, sistema de gestión para supermercado (Python, Tkinter y MySQL)
**Materia:** Proyecto ABP, Módulo Programador | **Institución:** ISPC, Tecnicatura Superior en Desarrollo de Software
**Grupo:** Comisión A | **Año:** 2026
**Repositorio:** https://github.com/andresitooliva34-eng/Supermercado.py

> Las semanas van de lunes a domingo. Las fechas, autores y códigos de commit salen del historial del repositorio (`git log`).

---

## 1. Integrantes y roles

| Rol | Integrante |
|-----|------------|
| Coordinador | Saravia, Samuel Eric |
| Modelo de datos | Lozano Bazán, Facundo Nicolás |
| Interfaz | Oliva Ruiz, Roberto Andrés |
| Acceso a datos | Oliva Ruiz, Roberto Andrés |
| Validaciones | Saravia, Samuel Eric |
| Documentación y pruebas | Marín Silva, Rafael Alejandro |

Roldán, Gabriel y Espeche, Brenda Aylen figuraban en el grupo al inicio. Desde el 12/10 ya no están en la lista de integrantes de la aplicación (commit `ca2cf66`).

---

## 2. Registro semanal de tareas

### Etapa inicial (antes del 16 de agosto)
- Reunión con el grupo para definir el proyecto y repartir los roles.
- Relevamiento de requerimientos y redacción de los requerimientos funcionales.
- Primer boceto del modelo E-R y paso al modelo relacional (Modelo de datos).
- **Responsables:** todo el grupo.

### Semana del 10 al 16 de agosto
- Primer commit con la estructura inicial del proyecto (`79faa8e`, 16/08). Esa primera versión guardaba los datos en JSON, tenía una conexión a una base MySQL llamada `supermercado` (`data/conexion.py`) y ya generaba comprobantes de compra en PDF (en `data/facturas/` hay tres del 15/08).
- El prototipo Tkinter permite agregar productos al carrito y registrar ventas: primeras ventas de prueba el 16/08.
- **Responsables:** Interfaz y Acceso a datos (Oliva Ruiz). **Evidencia:** commit `79faa8e`, `data/ventas.json`

### Semana del 17 al 23 de agosto
- Actualización del código (`eb38ce1`, 18/08, Oliva Ruiz).
- Pruebas del prototipo: ventas de prueba del 17/08 y del 23/08.
- **Responsables:** Oliva Ruiz (código); Documentación y pruebas (Marín Silva) y equipo (pruebas). **Evidencia:** commit `eb38ce1`, `data/ventas.json`

### Semana del 24 al 30 de agosto
- Actualización del proyecto (`ba9dc5c`, 27/08, Oliva Ruiz).

### Semana del 31 de agosto al 6 de septiembre
- No hay commits en el repositorio esta semana.

### Semana del 7 al 13 de septiembre
- Se saca la conexión a MySQL y la aplicación pasa a guardar todo en JSON (`2953c04`, 12/09, Oliva Ruiz).

### Semana del 14 al 20 de septiembre
- Mejoras de la interfaz: LabelFrame, Checkbutton, Scrollbar y confirmación al cerrar (`b8def1c`, 14/09, Oliva Ruiz). Es el último commit que tomó la primera devolución de Programación.
- Venta de prueba del 20/09.
- Capturas del prototipo (login, menú de administración, ABM de productos y categorías, confirmación de venta) para el informe.
- **Responsables:** Interfaz (Oliva Ruiz), Documentación y pruebas (Marín Silva). **Evidencia:** commit `b8def1c`, `data/ventas.json`

### Semana del 21 al 27 de septiembre
- Entrega del documento (21/09): resumen de avances, requerimientos funcionales, diccionario de datos con tipos y restricciones, políticas de borrado, normalización a 3FN y mejoras al diseño de la base de datos.
- 24/09, Oliva Ruiz: nueva versión de la aplicación con gestión de categorías y empleados (`8ace5a0`), README (`7c0d00a`) y limpieza del repositorio: se borran la carpeta build, los ejecutables, una carpeta temporal de pruebas y una imagen sobrante (`496a390`, `852e2f2`, `1d43542`, `815bf48`).
- 24/09, Saravia: actualiza `requirements.txt` con openpyxl (`b135484`).
- 27/09, Lozano Bazán: `requirements.txt` en UTF-8 y sin dependencias transitivas (`49c0d79`); validación de DNI y teléfono en los datos del cliente (`93d4966`, `bb0889a`).
- 27/09, Saravia: corrige la ventana de historial duplicada (`8297454`).
- Ventas de prueba con comprobante en PDF el 23/09 y el 24/09.
- **Responsables:** Modelo de datos (Lozano Bazán), Documentación y pruebas (Marín Silva) y Coordinación (Saravia) en el documento; los commits, según cada punto. **Evidencia:** documento de la Evidencia 5, `data/ventas.json`

### Semana del 28 de septiembre al 4 de octubre
- 28/09, Marín Silva: la aplicación ya no se puede usar sin iniciar sesión (`0cfb4f2`).
- 29/09, Saravia: corrige ventanas que se abrían duplicadas, como la de datos del cliente, y las bloquea con `grab_set` (`15fb0a9`, `f36728d`, `615ae72`).
- 29/09: ventas de prueba.
- 30/09, Marín Silva: corrige la lectura del ID en `buscar_por_id` y `siguiente_id` (`dd3da26`).
- 02/10, Lozano Bazán: al confirmar una venta, verifica el stock de todos los productos antes de descontar (`9955301`), y corrige la edición de empleados (`5296650`).
- **Evidencia:** commits de la semana, `data/ventas.json`

### Semana del 5 al 11 de octubre
- 06/10, Saravia: más correcciones de ventanas con `grab_set` (`4063b4a`).
- Instalación y configuración de MySQL Server 8.0 y acceso a la base desde Workbench y la terminal.
- Creación de la base `codemarket`: tablas, datos de prueba, integridad y roles de acceso (`schema.sql`).
- Módulo de conexión `data/conexion.py`, con la configuración en un archivo local que no se sube al repositorio.
- Alta y consulta de productos desde la interfaz con SQL propio (`logic/repositorio_productos.py` y `gui/ventana_productos.py`).
- Pruebas de integridad (errores de CHECK, UNIQUE y FOREIGN KEY) y de permisos con el usuario `cm_cajero`.
- 11/10, Oliva Ruiz: commit `0dbf786` ("Agrega base de datos MySQL, conexion y alta/consulta de productos"), merge `d49262d` con los commits de Saravia (`4063b4a`, `e052f4a`) y push a GitHub.
- **Responsables:** Acceso a datos (Oliva Ruiz); Saravia (ventanas). **Evidencia:** Evidencia 6

### Semana del 12 al 18 de octubre
- 12/10, Oliva Ruiz: actualiza la lista de integrantes del menú (`ca2cf66`).
- 13/10, Lozano Bazán: sube el script DDL coherente con el diccionario de datos (índices, campo `estado` en venta, clave con hash), las pruebas de integridad (`data/pruebas.sql`) y la ventana de productos adaptada a las tablas nuevas, que avisa cuando la base no está configurada (`762e784`); agrega el manual de usuario y actualiza el README (`c8bc439`).
- 13/10, Marín Silva: sube la bitácora (`1d80247`).
- 13/10, Oliva Ruiz: CRUD de productos (alta, consulta, modificación y baja) en la ventana Productos (MySQL) (`8c6b5a2`, `cf551a1`); adapta el CRUD a bases ya creadas con otros nombres de tabla (`761b2b0`); saca la bitácora del repositorio (`b81b3e0`).
- **Responsables:** Acceso a datos (Oliva Ruiz), Modelo de datos (Lozano Bazán), Documentación y pruebas (Marín Silva). **Evidencia:** commits de la semana

### Semana del 19 al 25 de octubre
- 21/10, Oliva Ruiz: la aplicación pasa a leer y escribir en MySQL las categorías, los clientes, los empleados y las ventas con su detalle (`logic/repositorio_mysql.py`); el esquema queda con nombres de tabla en plural; script para importar los JSON a MySQL (`logic/migrar_json_mysql.py`) y para actualizar bases existentes (`data/migracion_mysql.sql`) (`dc26366`).
- 21/10, Oliva Ruiz: cuenta de prueba admin / admin123 (`data/demo_admin.sql`), alta del primer administrador (`logic/configurar_administrador.py`), configuración de la conexión por variables de entorno, pruebas unitarias (`tests/`) e informe de evidencias actualizado en el repositorio (`08dd438`); manual de usuario ampliado (`42b12a6`).
- 21 y 22/10, Oliva Ruiz: corrige el informe según las devoluciones (estado de la persistencia y del inicio de sesión) y lo sube a las Evidencias 5 y 6.
- 22/10, Lozano Bazán: correcciones de la devolución de Base de Datos. Los datos de prueba de `schema.sql` coinciden con la Tabla 6.3 del informe (3 empleados: 1 administrador y 2 cajeros; la venta 5 anulada); vuelven las columnas `estado` y `numero_comprobante` de venta; se agregan los CHECK de rol y de medio de pago; el cajero ya no puede modificar clientes. Se agregan `data/verificar_datos.sql` (cantidades y permisos efectivos) y `data/pruebas_permisos.sql` (pruebas con el usuario `cm_cajero`), y se actualizan `data/pruebas.sql`, la migración, el README y esta bitácora.
- **Responsables:** Acceso a datos (Oliva Ruiz), Modelo de datos (Lozano Bazán). **Evidencia:** commits de la semana, Evidencias 5 y 6

---

## 3. Decisiones tomadas

| Decisión | Motivo |
|----------|--------|
| La aplicación se conecta con `cm_admin` y no con `root` | No usar la cuenta con todos los privilegios |
| La contraseña no va en el código: se lee de `data/config_db.json`, que está en `.gitignore` | Que cada integrante use la suya y no se suba al repositorio |
| MySQL genera las contraseñas de `cm_admin` y `cm_cajero` al crear la base (`RANDOM PASSWORD`) | Que no haya contraseñas fijas en el repositorio |
| El rol Cajero solo puede modificar la columna `stock` | Que no pueda cambiar precios ni borrar datos |
| Las ventas no se borran: se anulan con `estado = 'Anulada'` | Conservar el comprobante y la trazabilidad |
| Desde el 21/10 todos los módulos usan MySQL; los JSON quedan solo como respaldo y origen de la importación | Un solo catálogo: antes convivían dos que no se sincronizaban |
| En la base, las tablas se nombran en plural (`categorias`, `productos`, `ventas`…); el diccionario de datos usa el nombre de cada entidad en singular | Es el esquema que usan la aplicación y la migración, sin variantes |
| Cuenta de prueba admin / admin123, solo para demostración | Poder probar la aplicación sin crear usuarios; se cambia o desactiva antes de usar datos reales |

## 4. Dificultades encontradas y cómo se resolvieron

| Dificultad | Cómo se resolvió |
|------------|------------------|
| La contraseña de `root` había quedado escrita en el primer commit del repositorio | Se sacó del código y se pasó a un archivo local ignorado por Git; se recomienda cambiar esa contraseña porque sigue en el historial |
| El comando `mysql` no se reconocía en PowerShell | Se usó la ruta completa de `mysql.exe` |
| `git pull` rechazado por cambios locales en los JSON | Se guardaron aparte con `git stash`, se hizo el pull y se continuó |
| La terminal de Git Bash se trababa al pegar con Ctrl + V | Se pega con Shift + Insert o se escribe el comando a mano |
| Archivos de compilación (`build/`, `dist/`) y facturas listos para subir por error | Se sacaron de la preparación con `git restore --staged` y se agregaron los archivos de a uno |
| El script de la base no coincidía con el diccionario de datos | Se rehízo el DDL siguiendo el diccionario y se probó completo en MySQL 8.0 |
| La plantilla `config_db.example.json` tenía una contraseña real | Se reemplazó por `CONFIGURAR_LOCALMENTE` y MySQL genera las contraseñas al crear la base |
| El repositorio de productos se adaptaba a dos esquemas distintos (singular y plural) | Se unificó el esquema en plural y el CRUD usa solo las columnas de `schema.sql` |
| Las cantidades de registros del informe no coincidían con las de la base | Los datos de prueba de `schema.sql` se alinearon con la Tabla 6.3 y se agregó `data/verificar_datos.sql` para comprobarlas |
| La bitácora tenía datos sin completar | Se completó con el historial de commits del repositorio |
