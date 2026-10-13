# Manual de usuario — CodeMarket (Supermercado)

Este manual explica cómo usar el programa para registrar ventas y consultar
productos. No hace falta saber de computación: alcanza con seguir los pasos.

---

## 1. Para qué sirve

CodeMarket es un programa de caja para un supermercado. Permite:

- Ver los productos, su precio y cuántas unidades quedan (stock).
- Armar una venta agregando productos a un carrito.
- Cobrar con efectivo, tarjeta o Mercado Pago.
- Consultar las ventas realizadas y exportarlas a PDF o Excel.
- Administrar productos, categorías y empleados (según el cargo de cada persona).

---

## 2. Abrir el programa

1. Abrí el programa: desde la carpeta del proyecto, ejecutá `python main.py`. La primera vez hay que instalar lo que necesita, como explica el README.
2. Se abre la ventana principal y, enseguida, una ventana pidiendo usuario y contraseña.

---

## 3. Iniciar sesión

1. Escribí tu **Usuario** y tu **Contraseña**.
2. Hacé clic en **Ingresar** (o apretá Enter).

La primera vez se puede entrar con el usuario **admin** y la contraseña **admin123**.

- Si te equivocás, aparece el mensaje "Usuario o contraseña inválidos". Volvé a intentar.
- Arriba de la tabla de productos vas a ver tu nombre ("Cajero: ...") cuando hayas ingresado.
- Sin iniciar sesión se pueden mirar los productos, pero **no se puede finalizar una venta**.

---

## 4. La pantalla principal

De arriba hacia abajo:

- **Menú** (Archivo, Administración, Acerca de).
- **Filtros de búsqueda:** para encontrar productos.
- **Tabla de productos:** ID, nombre, categoría, precio, stock y estado.
  Los productos sin stock aparecen en rojo con el cartel **SIN STOCK**.
- **Botones de acción:** Cantidad, Agregar producto, Ver carrito, Finalizar venta, Historial y Datos del cliente.
- **Barra inferior:** cuántos productos hay en el carrito y el total a cobrar.

---

## 5. Buscar productos

- **Buscar por nombre:** escribí una parte del nombre (por ejemplo "leche"). La tabla se actualiza sola.
- **Categoría:** elegí una categoría de la lista para ver solo esa.
- **Solo con stock:** tildá la casilla para ocultar los productos agotados.
- **Limpiar filtros:** vuelve a mostrar todos los productos.

---

## 6. Registrar una venta, paso a paso

1. **Elegí el producto:** hacé clic sobre su fila en la tabla.
2. **Indicá la cantidad** en el casillero "Cantidad" (con las flechitas o escribiéndola).
3. Hacé clic en **Agregar producto**. Aparece el aviso "Producto agregado al carrito".
   Repetí los pasos 1 a 3 con cada producto de la venta.
4. (Opcional) Hacé clic en **Ver carrito** para revisar la venta. Ahí podés:
   - **Modificar** la cantidad: elegí el producto, escribí la nueva cantidad y hacé clic en Modificar.
   - **Eliminar** el producto seleccionado.
   - **Vaciar carrito** para empezar de nuevo.
5. (Opcional) **Datos del cliente:** completá nombre, apellido, DNI (7 u 8 números) y teléfono.
6. Hacé clic en **Finalizar venta**. Se muestra el total a pagar.
7. Elegí el medio de pago: **Efectivo**, **Tarjeta** o **Mercado Pago**.
8. Hacé clic en **Confirmar pago**. Aparece "Venta #... registrada".
   El stock de los productos se descuenta solo y el carrito queda vacío.

**Importante:** el programa no deja vender más unidades de las que hay.
Si pasa, aparece "No hay suficiente stock disponible": bajá la cantidad o elegí otro producto.

---

## 7. Ver el historial de ventas

- Hacé clic en **Historial**. Se muestra la lista de ventas, de la más nueva a la más vieja,
  con número de venta, cliente, total, fecha y medio de pago.
- Para guardarlo en un archivo, usá el menú **Archivo**:
  - **Exportar Historial a PDF**
  - **Exportar Historial a Excel**
  Elegí dónde guardar el archivo y hacé clic en Guardar.

---

## 8. Administración (según tu cargo)

El menú **Administración** muestra solo lo que tu cargo permite:

| Opción | Quiénes pueden usarla |
|--------|-----------------------|
| ABM de Productos (agregar, editar, eliminar, cambiar precio y stock) | Administrador, Gerente, Supervisor y Repositor |
| ABM de Categorías | Administrador, Gerente y Supervisor |
| ABM de Empleados | Administrador y Gerente |

En cada pantalla hay tres botones: **Nuevo**, **Editar** y **Eliminar**.
Para editar o eliminar, primero hacé clic sobre la fila.

- No se puede eliminar una categoría que todavía tiene productos.
- No podés eliminar tu propio usuario.

---

## 9. Consultar y cargar productos en la base de datos

En el menú **Archivo** → **Productos (MySQL)** se abre una ventana con:

- **Nuevo producto:** completá nombre, precio, stock y categoría, y hacé clic en **Guardar producto**.
- **Buscar por nombre o ID:** escribí y la lista se filtra al instante.

Para que funcione, el servidor de base de datos (MySQL) tiene que estar encendido.

---

## 10. Cerrar sesión y salir

- **Administración → Cerrar sesión** deja la caja lista para otra persona.
- Para salir, cerrá la ventana (la X) o usá **Archivo → Salir**. El programa pregunta
  "¿Cerrar la aplicación?": elegí **Sí**.

---

## 11. Mensajes frecuentes y qué hacer

| Mensaje | Qué significa | Qué hacer |
|---------|---------------|-----------|
| Seleccioná un producto de la tabla | No elegiste ningún producto | Hacé clic en una fila y volvé a intentar |
| No hay suficiente stock disponible | Pediste más unidades de las que hay | Bajá la cantidad |
| El carrito está vacío | Intentaste cobrar sin productos | Agregá al menos un producto |
| Iniciá sesión para registrar una venta | No ingresaste con tu usuario | Iniciá sesión desde el menú Administración |
| No hay stock suficiente de (producto). Revisá el carrito. | El stock de ese producto bajó después de que lo agregaste al carrito (por ejemplo, se cambió desde ABM de Productos) | Revisá el carrito y ajustá las cantidades |
| El DNI tiene que tener 7 u 8 números | El DNI tiene letras o la cantidad de números es incorrecta | Escribí solo números, sin puntos |
| No hay compras registradas para exportar | Todavía no hay ventas | Registrá una venta primero |
| No se pudo consultar / No se pudo guardar (ventana Productos MySQL) | El servidor de base de datos está apagado | Avisá a la persona que administra el sistema |
| Falta data/config_db.json (ventana Productos MySQL) | La base de datos no está configurada en esta computadora | Seguí los pasos de la sección de MySQL del README |

---

## 12. Consejos

- Revisá el carrito antes de **Confirmar pago**: después de confirmar no se puede deshacer desde esta pantalla.
- Cerrá la sesión al terminar el turno.
- Si algo no funciona como se explica acá, anotá el mensaje que aparece y avisá al equipo de soporte.
