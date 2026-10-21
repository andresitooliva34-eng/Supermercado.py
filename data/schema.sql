-- =====================================================================
-- CodeMarket - Sistema de gestión para supermercado
-- Script DDL completo: base, tablas, restricciones, índices, datos de
-- prueba y roles de acceso. Coherente con el diccionario de datos
-- (secciones 6, 7 y 10 del informe).
--
-- Uso (una sola vez, con el usuario administrador de MySQL):
--   mysql -u root -p --default-character-set=utf8mb4 < data/schema.sql
-- o, desde PowerShell:
--   mysql.exe -u root -p --default-character-set=utf8mb4 -e "source data/schema.sql"
--
-- ATENCIÓN: borra y vuelve a crear la base "codemarket" y los usuarios
-- cm_admin / cm_cajero. No toca ninguna otra base.
--
-- Contraseñas de los empleados de prueba (se guardan como hash bcrypt):
--   groldan / Admin123      ssaravia y flozano / Cajero123
-- =====================================================================

DROP DATABASE IF EXISTS codemarket;
CREATE DATABASE IF NOT EXISTS codemarket
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE codemarket;

-- =====================================================================
-- 1. TABLAS
-- =====================================================================

CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT NOT NULL,
    nombre       VARCHAR(50)        NOT NULL,
    CONSTRAINT pk_categoria PRIMARY KEY (id_categoria),
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
) ENGINE = InnoDB;

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT NOT NULL,
    nombre     VARCHAR(60)        NOT NULL,
    apellido   VARCHAR(60)        NOT NULL DEFAULT '',
    dni        VARCHAR(60)        NULL,
    telefono   VARCHAR(20)        NULL,
    email      VARCHAR(100)       NULL,
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_dni UNIQUE (dni)
) ENGINE = InnoDB;

CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT NOT NULL,
    nombre      VARCHAR(60)        NOT NULL,
    apellido    VARCHAR(60)        NOT NULL DEFAULT '',
    usuario     VARCHAR(30)        NOT NULL,
    rol         VARCHAR(20)        NOT NULL,
    clave       VARCHAR(255)       NOT NULL COMMENT 'Hash bcrypt, nunca la contraseña en texto plano',
    activo      TINYINT(1)         NOT NULL DEFAULT 1,
    CONSTRAINT pk_empleado PRIMARY KEY (id_empleado),
    CONSTRAINT uq_empleado_usuario UNIQUE (usuario)
) ENGINE = InnoDB;

CREATE TABLE productos (
    id_producto  INT AUTO_INCREMENT NOT NULL,
    codigo       VARCHAR(20)        NOT NULL,
    nombre       VARCHAR(100)       NOT NULL,
    precio       DECIMAL(10,2)      NOT NULL,
    stock        INT                NOT NULL DEFAULT 0,
    id_categoria INT                NOT NULL,
    CONSTRAINT pk_producto PRIMARY KEY (id_producto),
    CONSTRAINT uq_producto_codigo UNIQUE (codigo),
    CONSTRAINT chk_producto_precio CHECK (precio >= 0),
    CONSTRAINT chk_producto_stock  CHECK (stock >= 0),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE ventas (
    id_venta           INT AUTO_INCREMENT NOT NULL,
    fecha              DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_cliente         INT                NULL,
    id_empleado        INT                NOT NULL,
    metodo_pago        VARCHAR(20)        NOT NULL,
    total              DECIMAL(10,2)      NOT NULL,
    CONSTRAINT pk_venta PRIMARY KEY (id_venta),
    CONSTRAINT chk_venta_total CHECK (total >= 0),
    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
        ON DELETE SET NULL,
    CONSTRAINT fk_venta_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE detalle_venta (
    id_detalle      INT AUTO_INCREMENT NOT NULL,
    id_venta        INT                NOT NULL,
    id_producto     INT                NOT NULL,
    cantidad        INT                NOT NULL,
    precio_unitario DECIMAL(10,2)      NOT NULL COMMENT 'Precio histórico al momento de la venta',
    CONSTRAINT pk_detalle_venta PRIMARY KEY (id_detalle),
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_precio   CHECK (precio_unitario >= 0),
    CONSTRAINT fk_detalle_venta
        FOREIGN KEY (id_venta) REFERENCES ventas (id_venta)
        ON DELETE RESTRICT,
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- =====================================================================
-- 2. ÍNDICES (sección 10.4 del informe)
-- =====================================================================
-- Las PK, UNIQUE y FK ya generan sus propios índices en InnoDB.
CREATE INDEX idx_producto_nombre ON productos (nombre);   -- búsqueda por nombre
CREATE INDEX idx_venta_fecha     ON ventas (fecha);       -- reportes por período
CREATE INDEX idx_venta_cliente   ON ventas (id_cliente);  -- historial de un cliente

-- =====================================================================
-- 3. DATOS DE PRUEBA
-- =====================================================================

INSERT INTO categorias (nombre) VALUES
    ('Almacén'),
    ('Bebidas'),
    ('Lácteos'),
    ('Panadería');

INSERT INTO clientes (nombre, apellido, dni, telefono) VALUES
    ('Rafael', 'Marín', '30111222', '3511111111'),
    ('Andrés', 'Oliva', '30333444', '3512222222'),
    ('Facundo', 'Lozano', '33444555', NULL),
    ('Brenda', 'Espeche', '35666777', '3513333333');

INSERT INTO empleados (nombre, apellido, usuario, rol, clave) VALUES
    ('Gabriel', 'Roldán', 'groldan', 'administrador', '$2b$12$B5JN06CEkVSBet4h4kvfxOuRI/FPEKt4MtgWbyMVH234MhR4mtf/y'),
    ('Samuel', 'Saravia', 'ssaravia', 'cajero', '$2b$12$aYZW8v47Yzc64vRjFNgvHeRo26.6Tfoz3Pxqp9alw9JMfize6c1bu'),
    ('Facundo', 'Lozano', 'flozano', 'cajero', '$2b$12$tigejJjJCxtym3uUVbNHAuncCtrEQa9V5D6VXCrzybjboVeaQ5kWS');

INSERT INTO productos (codigo, nombre, precio, stock, id_categoria) VALUES
    ('LECHE-1L', 'Leche entera 1L', 1200.00, 50, 3),
    ('YOGUR-190G', 'Yogur natural 190g', 1200.00, 40, 3),
    ('QUESO-500G', 'Queso cremoso 500g', 5500.00, 25, 3),
    ('MANTECA-200G', 'Manteca 200g', 3200.00, 30, 3),
    ('PAN-LACTAL', 'Pan lactal blanco', 2500.00, 35, 4),
    ('MEDIALUNAS-6U', 'Medialunas de manteca 6u', 3500.00, 30, 4),
    ('ALFAJOR-CHOC', 'Alfajor de chocolate', 1500.00, 39, 4),
    ('GALLETAS-VAI', 'Galletitas de vainilla 400g', 2300.00, 35, 4),
    ('ARROZ-GALLO-1', 'Arroz Gallo Oro 1kg', 1800.00, 39, 1),
    ('FIDEOS-TIRA', 'Fideos Tirabuzón 500g', 1550.00, 42, 1),
    ('HARINA-000', 'Harina 000 1kg', 1200.00, 48, 1),
    ('AZUCAR-1KG', 'Azúcar 1kg', 1400.00, 55, 1),
    ('SAL-FINA-500', 'Sal fina 500g', 900.00, 56, 1),
    ('ACEITE-GIRA', 'Aceite de girasol 900ml', 3200.00, 40, 1),
    ('CEREALES', 'Cereales', 5700.00, 46, 1),
    ('AGUA-500ML', 'Agua mineral 500ml', 1000.00, 80, 2),
    ('GASEOSA-COLA', 'Gaseosa cola 1.5L', 3000.00, 50, 2),
    ('JUGO-NARANJA', 'Jugo de naranja 1L', 2200.00, 40, 2),
    ('AGUA-15L', 'Agua mineral 1.5L', 1500.00, 70, 2),
    ('SODA-15L', 'Soda 1.5L', 1400.00, 0, 2);

-- id_cliente NULL en la venta 3: consumidor final (sin cliente registrado)
INSERT INTO ventas (fecha, total, metodo_pago, id_cliente, id_empleado) VALUES
    ('2026-08-16 12:02:00', 8450.00, 'Tarjeta', 1, 2),
    ('2026-08-16 13:13:00', 6600.00, 'Tarjeta', 2, 2),
    ('2026-08-17 23:35:00', 10900.00, 'Transferencia', NULL, 3),
    ('2026-08-23 18:03:00', 3000.00, 'Efectivo', 3, 3),
    ('2026-08-24 10:20:00', 8000.00, 'Efectivo', 4, 2);

INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (1, 15, 1, 5700.00),
    (1, 10, 1, 1550.00),
    (1, 1, 1, 1200.00),
    (2, 17, 1, 3000.00),
    (2, 9, 2, 1800.00),
    (3, 9, 1, 1800.00),
    (3, 10, 2, 1550.00),
    (3, 11, 2, 1200.00),
    (3, 13, 4, 900.00),
    (4, 7, 2, 1500.00),
    (5, 3, 1, 5500.00),
    (5, 5, 1, 2500.00);

-- =====================================================================
-- 4. ROLES DE ACCESO
-- =====================================================================
-- Un ROL es un paquete de permisos que se asigna a los usuarios.
DROP ROLE IF EXISTS rol_administrador, rol_cajero;
DROP USER IF EXISTS 'cm_admin'@'localhost', 'cm_cajero'@'localhost';

CREATE ROLE rol_administrador, rol_cajero;

-- Administrador: todos los permisos sobre la base codemarket
GRANT ALL PRIVILEGES ON codemarket.* TO rol_administrador;

-- Cajero: consulta catálogo y clientes, registra clientes y ventas, y solo
-- puede modificar la columna stock de producto. No ve empleados, no cambia
-- precios, no anula ventas y no borra nada.
GRANT SELECT ON codemarket.productos       TO rol_cajero;
GRANT SELECT ON codemarket.categorias      TO rol_cajero;
GRANT SELECT, INSERT, UPDATE ON codemarket.clientes TO rol_cajero;
GRANT SELECT, INSERT ON codemarket.ventas          TO rol_cajero;
GRANT SELECT, INSERT ON codemarket.detalle_venta   TO rol_cajero;
GRANT UPDATE (stock) ON codemarket.productos       TO rol_cajero;

-- Usuarios de la aplicación (cambien estas contraseñas en su equipo)
CREATE USER 'cm_admin'@'localhost'  IDENTIFIED BY 'Admin_2026!';
CREATE USER 'cm_cajero'@'localhost' IDENTIFIED BY 'Cajero_2026!';

GRANT rol_administrador TO 'cm_admin'@'localhost';
GRANT rol_cajero        TO 'cm_cajero'@'localhost';
SET DEFAULT ROLE ALL TO 'cm_admin'@'localhost', 'cm_cajero'@'localhost';
