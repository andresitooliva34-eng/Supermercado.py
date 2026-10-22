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

-- Estado de la venta y número de comprobante, como en el diccionario de datos.
-- Las ventas que ya existen quedan con estado 'Completada'.
SET @agregar_estado = IF(
    EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'ventas'
          AND column_name = 'estado'
    ),
    'SELECT ''La columna ventas.estado ya existe'' AS estado',
    'ALTER TABLE ventas ADD COLUMN estado VARCHAR(10) NOT NULL DEFAULT ''Completada'' AFTER total, ADD CONSTRAINT chk_venta_estado CHECK (estado IN (''Completada'', ''Anulada''))'
);
PREPARE migracion_stmt FROM @agregar_estado;
EXECUTE migracion_stmt;
DEALLOCATE PREPARE migracion_stmt;

SET @agregar_comprobante = IF(
    EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'ventas'
          AND column_name = 'numero_comprobante'
    ),
    'SELECT ''La columna ventas.numero_comprobante ya existe'' AS estado',
    'ALTER TABLE ventas ADD COLUMN numero_comprobante VARCHAR(50) NULL AFTER estado, ADD CONSTRAINT uq_venta_comprobante UNIQUE (numero_comprobante)'
);
PREPARE migracion_stmt FROM @agregar_comprobante;
EXECUTE migracion_stmt;
DEALLOCATE PREPARE migracion_stmt;
