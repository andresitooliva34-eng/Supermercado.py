-- Actualiza la estructura existente de codemarket sin borrar sus datos.
-- Compatible con instalaciones antiguas del esquema plural de CodeMarket.
-- Se puede volver a ejecutar; las columnas existentes no se agregan otra vez.
USE codemarket;

ALTER TABLE clientes
    MODIFY dni VARCHAR(60) NULL;

ALTER TABLE empleados
    MODIFY rol VARCHAR(20) NOT NULL;

SET @agregar_clave = IF(
    EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'empleados'
          AND column_name = 'clave'
    ),
    'SELECT ''La columna empleados.clave ya existe'' AS estado',
    'ALTER TABLE empleados ADD COLUMN clave VARCHAR(255) NULL AFTER rol'
);
PREPARE migracion_stmt FROM @agregar_clave;
EXECUTE migracion_stmt;
DEALLOCATE PREPARE migracion_stmt;

SET @agregar_activo = IF(
    EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'empleados'
          AND column_name = 'activo'
    ),
    'SELECT ''La columna empleados.activo ya existe'' AS estado',
    'ALTER TABLE empleados ADD COLUMN activo TINYINT(1) NOT NULL DEFAULT 1 AFTER clave'
);
PREPARE migracion_stmt FROM @agregar_activo;
EXECUTE migracion_stmt;
DEALLOCATE PREPARE migracion_stmt;

ALTER TABLE ventas
    MODIFY metodo_pago VARCHAR(20) NOT NULL;
