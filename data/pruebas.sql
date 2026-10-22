-- =====================================================================
-- CodeMarket - Pruebas de integridad y reglas de negocio
-- Ejecutar DESPUÉS de schema.sql, como root, con --force para que siga
-- aunque haya errores (en las pruebas 1 a 9 el error es lo esperado):
--   mysql -u root -p --force --default-character-set=utf8mb4 < data/pruebas.sql
-- o, desde PowerShell:
--   mysql.exe -u root -p --force --default-character-set=utf8mb4 -e "source data/pruebas.sql"
-- Todas las pruebas terminan con ROLLBACK: la base queda igual que antes.
-- Los permisos del cajero se prueban aparte con data/pruebas_permisos.sql.
-- =====================================================================
USE codemarket;

-- Pruebas 1 a 9: MySQL tiene que rechazar cada sentencia.
START TRANSACTION;

-- 1 y 2: CHECK de precio y de stock (ERROR 3819)
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-PRECIO', 'Prueba', -5, 1, 1);
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-STOCK', 'Prueba', 10, -1, 1);

-- 3: FOREIGN KEY, categoría inexistente (ERROR 1452)
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-FK', 'Prueba', 10, 1, 99);

-- 4: UNIQUE, DNI repetido (ERROR 1062)
INSERT INTO clientes (nombre, apellido, dni)
VALUES ('Otro', 'Cliente', '30111222');

-- 5: CHECK de medio de pago (ERROR 3819)
INSERT INTO ventas (total, metodo_pago, id_empleado)
VALUES (100, 'Cheque', 1);

-- 6: CHECK de estado de la venta (ERROR 3819)
INSERT INTO ventas (total, metodo_pago, estado, id_empleado)
VALUES (100, 'Efectivo', 'Pendiente', 1);

-- 7: CHECK de rol del empleado (ERROR 3819)
INSERT INTO empleados (nombre, usuario, rol, clave)
VALUES ('Prueba', 'prueba_rol', 'invitado', 'hash');

-- 8 y 9: RESTRICT, no se borra lo que tiene datos asociados (ERROR 1451)
DELETE FROM categorias WHERE id_categoria = 3;
DELETE FROM ventas WHERE id_venta = 1;

ROLLBACK;

-- 10: SET NULL. Al borrar un cliente, su venta se conserva sin cliente.
START TRANSACTION;
DELETE FROM clientes WHERE id_cliente = 4;
SELECT id_venta, id_cliente, estado FROM ventas WHERE id_venta = 5;   -- id_cliente NULL
ROLLBACK;

-- 11: control de stock. 1 fila = descuenta; 0 filas = stock insuficiente.
START TRANSACTION;
UPDATE productos SET stock = stock - 1
 WHERE id_producto = 15 AND stock >= 1;
SELECT ROW_COUNT() AS filas_producto_15;     -- 1
UPDATE productos SET stock = stock - 99
 WHERE id_producto = 10 AND stock >= 99;
SELECT ROW_COUNT() AS filas_producto_10;     -- 0
ROLLBACK;

-- 12: anulación de una venta y reposición del stock (RN5).
START TRANSACTION;
UPDATE ventas SET estado = 'Anulada'
 WHERE id_venta = 1 AND estado = 'Completada';
SELECT ROW_COUNT() AS venta_anulada;         -- 1
UPDATE productos p
  JOIN detalle_venta d ON d.id_producto = p.id_producto
   SET p.stock = p.stock + d.cantidad
 WHERE d.id_venta = 1;
SELECT ROW_COUNT() AS productos_repuestos;   -- 3 (50 -> 51, 42 -> 43 y 46 -> 47)
UPDATE ventas SET estado = 'Anulada'
 WHERE id_venta = 1 AND estado = 'Completada';
SELECT ROW_COUNT() AS segunda_anulacion;     -- 0: ya estaba anulada
ROLLBACK;
