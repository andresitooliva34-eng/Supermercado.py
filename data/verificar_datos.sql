-- =====================================================================
-- CodeMarket - Verificación de los datos de prueba y de los permisos
-- Ejecutar como root después de schema.sql:
--   mysql -u root -p --default-character-set=utf8mb4 < data/verificar_datos.sql
-- o, desde PowerShell:
--   mysql.exe -u root -p --default-character-set=utf8mb4 -e "source data/verificar_datos.sql"
-- En una base recién creada, las cantidades tienen que coincidir con la
-- Tabla 6.3 del informe: 4 categorías, 4 clientes, 3 empleados,
-- 20 productos, 5 ventas y 12 detalles de venta.
-- =====================================================================
USE codemarket;

-- Cantidad de registros por tabla
SELECT 'categorias' AS tabla, COUNT(*) AS filas FROM categorias
UNION ALL SELECT 'clientes', COUNT(*) FROM clientes
UNION ALL SELECT 'empleados', COUNT(*) FROM empleados
UNION ALL SELECT 'productos', COUNT(*) FROM productos
UNION ALL SELECT 'ventas', COUNT(*) FROM ventas
UNION ALL SELECT 'detalle_venta', COUNT(*) FROM detalle_venta;

-- Empleados por rol: 1 administrador y 2 cajeros
SELECT rol, COUNT(*) AS empleados FROM empleados GROUP BY rol ORDER BY rol;

-- Venta 3 a consumidor final (id_cliente NULL) y venta 5 anulada
SELECT id_venta, id_cliente, metodo_pago, estado FROM ventas WHERE id_venta IN (3, 5);

-- Producto sin stock
SELECT id_producto, nombre, stock FROM productos WHERE stock = 0;

-- Permisos efectivos del cajero, con el rol aplicado
SHOW GRANTS FOR 'cm_cajero'@'localhost' USING rol_cajero;
