# Bitácora de equipo — CodeMarket

**Proyecto:** CodeMarket, sistema de gestión para supermercado (Python, Tkinter y MySQL)
**Materia:** Proyecto ABP, Módulo Programador | **Institución:** ISPC, Tecnicatura Superior en Desarrollo de Software
**Grupo:** Comisión A | **Año:** 2026
**Repositorio:** https://github.com/andresitooliva34-eng/Supermercado.py

> Las semanas van de lunes a domingo. Los datos marcados con **[completar]**
> no se pudieron verificar y hay que cargarlos con `git log` (ver el final).
> Los responsables de cada tarea se asignaron según el reparto de roles del
> informe (sección 3): confirmarlos con el grupo antes de entregar.

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
| Otros integrantes | Roldán, Gabriel; Espeche, Brenda Aylen: **[completar tareas]** |

---

## 2. Registro semanal de tareas

### Etapa inicial (fechas a completar)
- Reunión con el grupo para definir el proyecto y repartir los roles.
- Relevamiento de requerimientos y redacción de los requerimientos funcionales.
- Primer boceto del modelo E-R y paso al modelo relacional (Modelo de datos).
- Estructura inicial del repositorio (commit `79faa8e`, "Primer commit: estructura inicial").
- **Responsables:** todo el grupo. **Fechas:** [completar]

### Semana del 10 al 16 de agosto
- El prototipo Tkinter ya permite agregar productos al carrito y registrar ventas: queda la primera venta de prueba (16/08).
- **Responsables:** Interfaz y Acceso a datos (Oliva Ruiz). **Evidencia:** `data/ventas.json`

### Semana del 17 al 23 de agosto
- Pruebas del prototipo: ventas de prueba del 17/08 y del 23/08 con distintos medios de pago.
- **Responsables:** Documentación y pruebas (Marín Silva) y equipo. **Evidencia:** `data/ventas.json`

### Del 24 de agosto al 13 de septiembre
- Sin registros verificables. **[completar]** (por ejemplo: correcciones del modelo E-R y de las pantallas según la devolución docente, ABM de productos, categorías y empleados, validaciones de DNI y teléfono).

### Semana del 14 al 20 de septiembre
- Comprobante de compra en PDF funcionando (primer comprobante generado el 20/09).
- Capturas del prototipo (login, menú de administración, ABM de productos y categorías, confirmación de venta) para el informe.
- **Responsables:** Interfaz (Oliva Ruiz), Documentación y pruebas (Marín Silva). **Evidencia:** `data/facturas/`

### Semana del 21 al 27 de septiembre
- Entrega del documento (21/09): resumen de avances, requerimientos funcionales, diccionario de datos con tipos y restricciones, políticas de borrado, normalización a 3FN y mejoras al diseño de la base de datos.
- Más pruebas de ventas con comprobante (23 y 24/09).
- **Responsables:** Modelo de datos (Lozano Bazán), Documentación y pruebas (Marín Silva), Coordinación (Saravia). **Evidencia:** documento de la Evidencia 5

### Semana del 28 de septiembre al 4 de octubre
- Sin registros verificables. **[completar]**

### Semana del 5 al 11 de octubre
- Instalación y configuración de MySQL Server 8.0 y acceso a la base desde Workbench y la terminal.
- Creación de la base `codemarket`: tablas, datos de prueba, integridad y roles de acceso (`schema.sql`).
- Módulo de conexión `data/conexion.py`, con la configuración en un archivo local que no se sube al repositorio.
- Alta y consulta de productos desde la interfaz con SQL propio (`logic/repositorio_productos.py` y `gui/ventana_productos.py`).
- Pruebas de integridad (errores de CHECK, UNIQUE y FOREIGN KEY) y de permisos con el usuario `cm_cajero`.
- Commit `0dbf786` ("Agrega base de datos MySQL, conexion y alta/consulta de productos"); merge `d49262d` con 2 commits de otros integrantes (`e052f4a`) y push a GitHub.
- **Responsables:** Acceso a datos (Oliva Ruiz). **Evidencia:** Evidencia 6

### Semana del 12 al 18 de octubre (en curso)
- Atención de la devolución de la cátedra: script DDL completo y coherente con el diccionario de datos (tablas en singular, índices, campo `estado` en venta, clave con hash), reglas de negocio en la minuta y unificación de lo declarado sobre persistencia y contraseñas.
- Informe actualizado, manual de usuario y bitácora.
- **Responsables:** Acceso a datos (Oliva Ruiz) y Modelo de datos (Lozano Bazán): **[confirmar con el grupo]**

---

## 3. Decisiones tomadas

| Decisión | Motivo |
|----------|--------|
| La aplicación se conecta con `cm_admin` y no con `root` | No usar la cuenta con todos los privilegios |
| La contraseña no va en el código: se lee de `data/config_db.json`, que está en `.gitignore` | Que cada integrante use la suya y no se suba al repositorio |
| El rol Cajero solo puede modificar la columna `stock` | Que no pueda cambiar precios ni borrar datos |
| Las ventas no se borran: se anulan con `estado = 'Anulada'` | Conservar el comprobante y la trazabilidad |
| Se mantiene JSON como respaldo hasta migrar todos los módulos a MySQL | No frenar el desarrollo del resto del equipo |

## 4. Dificultades encontradas y cómo se resolvieron

| Dificultad | Cómo se resolvió |
|------------|------------------|
| La contraseña de `root` había quedado escrita en el primer commit del repositorio | Se sacó del código y se pasó a un archivo local ignorado por Git; se recomienda cambiar esa contraseña porque sigue en el historial |
| El comando `mysql` no se reconocía en PowerShell | Se usó la ruta completa de `mysql.exe` |
| `git pull` rechazado por cambios locales en los JSON | Se guardaron aparte con `git stash`, se hizo el pull y se continuó |
| La terminal de Git Bash se trababa al pegar con Ctrl + V | Se pega con Shift + Insert o se escribe el comando a mano |
| Archivos de compilación (`build/`, `dist/`) y facturas listos para subir por error | Se sacaron de la preparación con `git restore --staged` y se agregaron los archivos de a uno |
| El script de la base no coincidía con el diccionario de datos | Se rehízo el DDL siguiendo el diccionario y se probó completo en MySQL 8.0 |

---

## 5. Cómo completar las fechas y los autores con Git

Ejecutar en Git Bash dentro de la carpeta del proyecto y pegar el resultado en las semanas marcadas:

```
git log --pretty=format:"%ad | %an | %s" --date=short
```

Cada línea muestra la fecha, el autor y el mensaje de un commit.

---

## 6. Reuniones de equipo

| Fecha | Temas tratados | Asistentes |
|-------|----------------|------------|
| [completar] | [completar] | [completar] |
