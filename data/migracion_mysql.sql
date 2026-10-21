-- Actualiza la estructura existente de codemarket sin borrar sus datos.
-- Ejecutar una sola vez con un usuario que tenga permisos ALTER.
USE codemarket;

ALTER TABLE clientes
    MODIFY dni VARCHAR(60) NULL;

ALTER TABLE empleados
    MODIFY rol VARCHAR(20) NOT NULL,
    ADD COLUMN clave VARCHAR(255) NULL AFTER rol,
    ADD COLUMN activo TINYINT(1) NOT NULL DEFAULT 1 AFTER clave;

ALTER TABLE ventas
    MODIFY metodo_pago VARCHAR(20) NOT NULL;
