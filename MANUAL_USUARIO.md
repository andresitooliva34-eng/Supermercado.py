MANUAL DE USUARIO — CODEMARKET

Sistema de gestión para supermercado

Tecnologías: Python, Tkinter y MySQL

Institución: ISPC — Tecnicatura Superior en Desarrollo de Software

Proyecto ABP · Comisión A · 2026

Este manual explica cómo utilizar CodeMarket para consultar productos y registrar ventas. Seguí los pasos en orden. Los nombres exactos de algunos botones pueden variar según la versión instalada.

1. ¿Para qué sirve?

CodeMarket es una aplicación de escritorio para la operación de caja y la administración del supermercado. Según el usuario y los permisos asignados, permite:

Consultar productos, precios, categorías y existencias.

Agregar productos a un carrito y registrar ventas.

Seleccionar efectivo, tarjeta o Mercado Pago como medio de pago.

Consultar el historial y exportarlo a PDF o Excel.

Administrar productos, categorías y empleados, según el rol.

2. Abrir el programa

Abrí la aplicación SuperMercado (ícono del carrito verde).

Esperá a que aparezca la ventana de inicio de sesión.

Si la aplicación no abre o muestra un error de conexión, avisá a la persona responsable de la instalación.

3. Iniciar sesión

Escribí tu usuario y contraseña.

Hacé clic en Ingresar o presioná Enter.

Para la demostración académica se documentó el usuario admin y la contraseña admin123. Estas credenciales solo deben utilizarse en el entorno de prueba; no son seguras para producción.

Si aparece “Usuario o contraseña inválidos”, revisá los datos e intentá nuevamente.

Una vez iniciada la sesión, la pantalla puede mostrar el usuario o el rol activo. Para finalizar una venta es necesario iniciar sesión.

4. Pantalla principal

La pantalla de caja puede incluir:

Menú: opciones de archivo, administración y acerca de.

Filtros: permiten buscar por nombre o categoría y limitar la lista a productos con stock.

Tabla de productos: muestra datos como identificador, nombre, categoría, precio y stock.

Acciones de venta: cantidad, agregar producto, ver carrito y finalizar venta.

Historial y datos del cliente: permiten consultar ventas o cargar datos del comprador.

Resumen del carrito: indica la cantidad de artículos y el total estimado.

La apariencia y los controles disponibles dependen de la versión de la aplicación y de los permisos del usuario.

5. Buscar productos

Por nombre: escribí una parte del nombre del producto, por ejemplo leche.

Por categoría: elegí una categoría en el filtro, si está disponible.

Solo con stock: activá la casilla para ocultar productos agotados, si aparece en pantalla.

Limpiar filtros: usá esta opción para volver a ver la lista completa.

6. Registrar una venta

Seleccioná un producto en la tabla.

Indicá la cantidad en el campo Cantidad.

Hacé clic en Agregar producto.

Repetí los pasos para cada artículo que quiera comprar el cliente.

Entrá en Ver carrito para revisar los artículos. Si la pantalla lo permite, modificá cantidades, quitá artículos o vaciá el carrito.

Si corresponde, completá los datos del cliente. El DNI debe ingresarse solo con números, sin puntos, y tener 7 u 8 dígitos si esa validación está habilitada.

Hacé clic en Finalizar venta y revisá el total.

Elegí Efectivo, Tarjeta o Mercado Pago, según las opciones que muestre la aplicación.

Hacé clic en Confirmar pago y esperá el mensaje de confirmación.

Si la operación se registra correctamente, la aplicación informa el número de venta. Verificá que el carrito quede vacío y que el stock se actualice.

Control de stock: no intentes registrar una cantidad mayor a la disponible. Si el sistema informa que no hay stock suficiente o que el stock cambió, revisá el carrito y ajustá las cantidades antes de confirmar.

7. Consultar y exportar el historial

Hacé clic en Historial.

Revisá los datos que muestra la lista, como número de venta, cliente, total, fecha y medio de pago, según la versión.

Para exportar, abrí el menú Archivo y elegí Exportar Historial a PDF o Exportar Historial a Excel, si esas opciones están disponibles.

Seleccioná la carpeta de destino y guardá el archivo.

Si no hay ventas registradas, no habrá operaciones para exportar.

8. Administración y permisos

El menú Administración puede mostrar distintas opciones según el rol configurado. La matriz de permisos documentada para el proyecto es:

Opción

Roles habilitados según la documentación del proyecto

ABM de productos

Administrador, Gerente, Supervisor y Repositor

ABM de categorías

Administrador, Gerente y Supervisor

ABM de empleados

Administrador y Gerente

ABM significa Alta, Baja y Modificación. Para editar o eliminar, seleccioná primero el registro correspondiente. Respetá los mensajes de validación del sistema; por ejemplo, una categoría que todavía tiene productos asociados puede no ser eliminable.

Los permisos efectivos dependen de cómo esté configurada la versión instalada. Si una opción no aparece, consultá al administrador del sistema.

9. Ventana de prueba de productos en MySQL

En las versiones que incluyen la opción Archivo → Productos (MySQL), esta ventana permite probar la consulta y el alta de productos directamente en la base de datos:

Comprobá que el servicio de MySQL esté iniciado y que la conexión esté configurada.

Para crear un producto, completá los campos solicitados, incluida la categoría, y presioná Guardar producto.

Para buscar, escribí el nombre o ID en el campo de búsqueda, si está disponible.

Si aparece un error de conexión o de consulta, no repitas la operación muchas veces: avisá a la persona responsable de la base de datos.

Importante: esta ventana debe tratarse como una función de administración/prueba si aparece separada de la caja principal. No cargues el mismo producto por dos caminos distintos sin confirmar cuál es la fuente de datos operativa definida para la versión instalada.

10. Cerrar sesión y salir

Si está disponible Administración → Cerrar sesión, usalo al terminar el turno.

Para cerrar la aplicación, hacé clic en la X o elegí Archivo → Salir, si aparece esa opción.

Si se muestra una confirmación, elegí Sí para salir.

11. Mensajes frecuentes

Mensaje o situación

Qué hacer

Seleccioná un producto de la tabla

Seleccioná una fila antes de agregar un artículo.

No hay suficiente stock disponible

Reducí la cantidad o elegí otro producto.

El carrito está vacío

Agregá al menos un producto antes de finalizar la venta.

Iniciá sesión para registrar una venta

Iniciá sesión con una cuenta habilitada.

El stock cambió. Revisá el carrito

Revisá las cantidades y volvé a intentar.

El DNI tiene que tener 7 u 8 números

Ingresá solo números, sin puntos, si el campo requiere DNI.

No hay compras registradas para exportar

Registrá una venta antes de exportar el historial.

No se pudo consultar o guardar en Productos (MySQL)

Comprobá que MySQL esté iniciado y avisá al administrador si continúa el error.

12. Buenas prácticas

Revisá el carrito y el total antes de confirmar el pago.

No cierres la aplicación durante el registro de una venta.

Cerrá la sesión al terminar el turno.

No compartas contraseñas personales ni uses la cuenta de demostración fuera de las pruebas.

Si algo no funciona, anotá el mensaje exacto y comunicáselo al equipo de soporte.
