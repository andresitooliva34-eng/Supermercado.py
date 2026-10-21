-- Pruebas de integridad. Ejecutar DESPUÉS de schema.sql como root:
-- mysql.exe -u root -p --force --default-character-set=utf8mb4 -e "source data/pruebas.sql"
USE codemarket;

-- CHECK de precio y stock (ERROR 3819).
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-PRECIO', 'Prueba', -5, 1, 1);
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-STOCK', 'Prueba', 10, -1, 1);

-- FOREIGN KEY de categoría (ERROR 1452).
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria)
VALUES ('PRUEBA-FK', 'Prueba', 10, 1, 99);

-- UNIQUE de DNI (ERROR 1062).
INSERT INTO clientes (nombre, apellido, dni)
VALUES ('Otro Cliente', '', '30111222');

-- RESTRICT: las categorías y productos referenciados no se borran (ERROR 1451).
DELETE FROM categorias WHERE id_categoria = 3;
DELETE FROM ventas WHERE id_venta = 1;

-- SET NULL de cliente, se deshace con ROLLBACK.
START TRANSACTION;
DELETE FROM clientes WHERE id_cliente = 4;
SELECT id_venta, id_cliente FROM ventas WHERE id_venta = 5;
ROLLBACK;

-- Descuento de stock: una fila actualizada; luego cero por stock insuficiente.
START TRANSACTION;
UPDATE productos SET stock = stock - 1
WHERE id_producto = 15 AND stock >= 1;
SELECT ROW_COUNT() AS filas_producto_15;
UPDATE productos SET stock = stock - 99
WHERE id_producto = 10 AND stock >= 99;
SELECT ROW_COUNT() AS filas_producto_10;
ROLLBACK;

-- Un cajero no puede cambiar precios ni eliminar productos.
-- UPDATE productos SET precio = 1 WHERE id_producto = 1; -> ERROR 1143
-- DELETE FROM productos WHERE id_producto = 1;            -> ERROR 1142
