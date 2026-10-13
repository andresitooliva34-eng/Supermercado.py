-- =====================================================================
-- CodeMarket - Pruebas de integridad y reglas de negocio
-- Ejecutar DESPUES de schema.sql, como root, con --force para que siga
-- aunque haya errores (los errores son lo esperado en las pruebas 1 a 8):
--   mysql.exe -u root -p --force --default-character-set=utf8mb4 -e "source data/pruebas.sql"
-- =====================================================================
USE codemarket;

-- 1 y 2: CHECK de precio y stock (ERROR 3819)
INSERT INTO producto (nombre, precio, stock, id_categoria) VALUES ('Prueba', -5, 1, 1);
INSERT INTO producto (nombre, precio, stock, id_categoria) VALUES ('Prueba', 10, -1, 1);
-- 3: FOREIGN KEY, categoria inexistente (ERROR 1452)
INSERT INTO producto (nombre, precio, stock, id_categoria) VALUES ('Prueba', 10, 1, 99);
-- 4: UNIQUE, DNI repetido (ERROR 1062)
INSERT INTO cliente (nombre, dni) VALUES ('Otro Cliente', '30111222');
-- 5 y 6: CHECK de metodo_pago y de rol (ERROR 3819)
INSERT INTO venta (total, metodo_pago, id_empleado) VALUES (100, 'Cheque', 1);
INSERT INTO empleado (nombre, rol, usuario, clave) VALUES ('X', 'Gerente', 'x', 'h');
-- 7 y 8: RESTRICT, no se borra lo que tiene datos asociados (ERROR 1451)
DELETE FROM categoria WHERE id_categoria = 3;
DELETE FROM venta WHERE id_venta = 1;

-- 9: SET NULL, al borrar un cliente la venta se conserva (se deshace con ROLLBACK)
START TRANSACTION;
DELETE FROM cliente WHERE id_cliente = 4;
SELECT id_venta, id_cliente, estado FROM venta WHERE id_venta = 5;
ROLLBACK;

-- 10: control de stock. 1 fila = descuenta; 0 filas = stock insuficiente
START TRANSACTION;
UPDATE producto SET stock = stock - 1  WHERE id_producto = 15 AND stock >= 1;
SELECT ROW_COUNT() AS filas_producto_15;
UPDATE producto SET stock = stock - 99 WHERE id_producto = 10 AND stock >= 99;
SELECT ROW_COUNT() AS filas_producto_10;
ROLLBACK;

-- 11: anulacion de venta y reposicion de stock (se deshace con ROLLBACK)
START TRANSACTION;
UPDATE venta SET estado = 'Anulada' WHERE id_venta = 1 AND estado = 'Completada';
SELECT ROW_COUNT() AS venta_anulada;
UPDATE producto p JOIN detalle_venta d ON d.id_producto = p.id_producto
   SET p.stock = p.stock + d.cantidad WHERE d.id_venta = 1;
SELECT ROW_COUNT() AS productos_repuestos;
UPDATE venta SET estado = 'Anulada' WHERE id_venta = 1 AND estado = 'Completada';
SELECT ROW_COUNT() AS segunda_anulacion;
ROLLBACK;

-- Pruebas de ROLES: abrir sesion como cm_cajero (clave Cajero_2026!) y probar:
--   UPDATE producto SET precio = 1 WHERE id_producto = 1;   -> ERROR 1143
--   SELECT * FROM empleado;                                 -> ERROR 1142
--   DELETE FROM producto WHERE id_producto = 1;             -> ERROR 1142
--   UPDATE venta SET estado = 'Anulada' WHERE id_venta = 1; -> ERROR 1142
