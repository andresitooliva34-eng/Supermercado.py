-- =====================================================================
-- CodeMarket - Verificación de los permisos del rol cajero
-- Ejecutar conectado como cm_cajero (no como root), con --force:
--   mysql -u cm_cajero -p --force --default-character-set=utf8mb4 < data/pruebas_permisos.sql
-- o, desde PowerShell:
--   mysql.exe -u cm_cajero -p --force --default-character-set=utf8mb4 -e "source data/pruebas_permisos.sql"
-- La contraseña de cm_cajero la muestra MySQL al ejecutar schema.sql. Si no
-- la guardaste, root le puede poner una contraseña local (no se sube a GitHub):
--   ALTER USER 'cm_cajero'@'localhost' IDENTIFIED BY 'tu_clave_local';
-- Lo permitido se deshace con ROLLBACK: la base queda igual que antes.
-- =====================================================================
USE codemarket;

SELECT CURRENT_USER() AS usuario, CURRENT_ROLE() AS rol;   -- cm_cajero@localhost con rol_cajero

-- PERMITIDO: consultar el catálogo y los clientes
SELECT id_producto, nombre, stock FROM productos ORDER BY id_producto LIMIT 3;
SELECT COUNT(*) AS clientes FROM clientes;

-- PERMITIDO: registrar un cliente y descontar stock (se deshace con ROLLBACK)
START TRANSACTION;
INSERT INTO clientes (nombre, apellido, dni) VALUES ('Cliente', 'Prueba', '40111222');
SELECT ROW_COUNT() AS cliente_registrado;    -- 1
UPDATE productos SET stock = stock - 1 WHERE id_producto = 1;
SELECT ROW_COUNT() AS stock_descontado;      -- 1
ROLLBACK;

-- RECHAZADO: MySQL tiene que dar error en cada sentencia
UPDATE productos SET precio = 1 WHERE id_producto = 1;     -- ERROR 1143: no cambia precios
UPDATE clientes SET telefono = '0' WHERE id_cliente = 1;   -- ERROR 1142: no modifica clientes
DELETE FROM productos WHERE id_producto = 1;               -- ERROR 1142: no borra productos
SELECT * FROM empleados;                                   -- ERROR 1142: no ve empleados
UPDATE ventas SET estado = 'Anulada' WHERE id_venta = 1;   -- ERROR 1142: no anula ventas
DELETE FROM ventas WHERE id_venta = 1;                     -- ERROR 1142: no borra ventas
