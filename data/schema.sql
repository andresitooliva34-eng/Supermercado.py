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

CREATE TABLE categoria (
    id_categoria INT AUTO_INCREMENT NOT NULL,
    nombre       VARCHAR(50)        NOT NULL,
    CONSTRAINT pk_categoria PRIMARY KEY (id_categoria),
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
) ENGINE = InnoDB;

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT NOT NULL,
    nombre     VARCHAR(100)       NOT NULL,
    dni        VARCHAR(15)        NOT NULL,
    telefono   VARCHAR(20)        NULL,
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cliente_dni UNIQUE (dni)
) ENGINE = InnoDB;

CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT NOT NULL,
    nombre      VARCHAR(100)       NOT NULL,
    rol         VARCHAR(20)        NOT NULL,
    usuario     VARCHAR(50)        NOT NULL,
    clave       VARCHAR(255)       NOT NULL COMMENT 'Hash bcrypt, nunca la contraseña en texto plano',
    CONSTRAINT pk_empleado PRIMARY KEY (id_empleado),
    CONSTRAINT uq_empleado_usuario UNIQUE (usuario),
    CONSTRAINT chk_empleado_rol CHECK (rol IN ('Administrador', 'Cajero'))
) ENGINE = InnoDB;

CREATE TABLE producto (
    id_producto  INT AUTO_INCREMENT NOT NULL,
    nombre       VARCHAR(100)       NOT NULL,
    precio       DECIMAL(10,2)      NOT NULL,
    stock        INT                NOT NULL DEFAULT 0,
    id_categoria INT                NOT NULL,
    CONSTRAINT pk_producto PRIMARY KEY (id_producto),
    CONSTRAINT chk_producto_precio CHECK (precio >= 0),
    CONSTRAINT chk_producto_stock  CHECK (stock >= 0),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE venta (
    id_venta           INT AUTO_INCREMENT NOT NULL,
    fecha              DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total              DECIMAL(10,2)      NOT NULL,
    metodo_pago        VARCHAR(20)        NOT NULL,
    estado             VARCHAR(10)        NOT NULL DEFAULT 'Completada',
    numero_comprobante VARCHAR(50)        NULL,
    id_cliente         INT                NULL     COMMENT 'NULL = consumidor final',
    id_empleado        INT                NOT NULL,
    CONSTRAINT pk_venta PRIMARY KEY (id_venta),
    CONSTRAINT uq_venta_comprobante UNIQUE (numero_comprobante),
    CONSTRAINT chk_venta_total CHECK (total >= 0),
    CONSTRAINT chk_venta_metodo_pago
        CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    CONSTRAINT chk_venta_estado CHECK (estado IN ('Completada', 'Anulada')),
    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente (id_cliente)
        ON DELETE SET NULL,
    CONSTRAINT fk_venta_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
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
        FOREIGN KEY (id_venta) REFERENCES venta (id_venta)
        ON DELETE RESTRICT,
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON DELETE RESTRICT
) ENGINE = InnoDB;

-- =====================================================================
-- 2. ÍNDICES (sección 10.4 del informe)
-- =====================================================================
-- Las PK, UNIQUE y FK ya generan sus propios índices en InnoDB.
CREATE INDEX idx_producto_nombre ON producto (nombre);   -- búsqueda por nombre
CREATE INDEX idx_venta_fecha     ON venta (fecha);       -- reportes por período
CREATE INDEX idx_venta_cliente   ON venta (id_cliente);  -- historial de un cliente

-- =====================================================================
-- 3. DATOS DE PRUEBA
-- =====================================================================

INSERT INTO categoria (nombre) VALUES
    ('Almacén'),
    ('Bebidas'),
    ('Lácteos'),
    ('Panadería');

INSERT INTO cliente (nombre, dni, telefono) VALUES
    ('Rafael Marín', '30111222', '3511111111'),
    ('Andrés Oliva', '30333444', '3512222222'),
    ('Facundo Lozano', '33444555', NULL),
    ('Brenda Espeche', '35666777', '3513333333');

INSERT INTO empleado (nombre, rol, usuario, clave) VALUES
    ('Gabriel Roldán', 'Administrador', 'groldan', '$2b$12$B5JN06CEkVSBet4h4kvfxOuRI/FPEKt4MtgWbyMVH234MhR4mtf/y'),
    ('Samuel Saravia', 'Cajero', 'ssaravia', '$2b$12$aYZW8v47Yzc64vRjFNgvHeRo26.6Tfoz3Pxqp9alw9JMfize6c1bu'),
    ('Facundo Lozano', 'Cajero', 'flozano', '$2b$12$tigejJjJCxtym3uUVbNHAuncCtrEQa9V5D6VXCrzybjboVeaQ5kWS');

INSERT INTO producto (nombre, precio, stock, id_categoria) VALUES
    ('Leche entera 1L', 1200.00, 50, 3),
    ('Yogur natural 190g', 1200.00, 40, 3),
    ('Queso cremoso 500g', 5500.00, 25, 3),
    ('Manteca 200g', 3200.00, 30, 3),
    ('Pan lactal blanco', 2500.00, 35, 4),
    ('Medialunas de manteca 6u', 3500.00, 30, 4),
    ('Alfajor de chocolate', 1500.00, 39, 4),
    ('Galletitas de vainilla 400g', 2300.00, 35, 4),
    ('Arroz Gallo Oro 1kg', 1800.00, 39, 1),
    ('Fideos Tirabuzón 500g', 1550.00, 42, 1),
    ('Harina 000 1kg', 1200.00, 48, 1),
    ('Azúcar 1kg', 1400.00, 55, 1),
    ('Sal fina 500g', 900.00, 56, 1),
    ('Aceite de girasol 900ml', 3200.00, 40, 1),
    ('Cereales', 5700.00, 46, 1),
    ('Agua mineral 500ml', 1000.00, 80, 2),
    ('Gaseosa cola 1.5L', 3000.00, 50, 2),
    ('Jugo de naranja 1L', 2200.00, 40, 2),
    ('Agua mineral 1.5L', 1500.00, 70, 2),
    ('Soda 1.5L', 1400.00, 0, 2);

-- id_cliente NULL en la venta 3: consumidor final (sin cliente registrado)
-- La venta 5 está anulada: se conserva como historial, nunca se borra.
INSERT INTO venta (fecha, total, metodo_pago, estado, numero_comprobante, id_cliente, id_empleado) VALUES
    ('2026-08-16 12:02:00', 8450.00, 'Tarjeta', 'Completada', 'factura_2026-08-16_12-02-00.pdf', 1, 2),
    ('2026-08-16 13:13:00', 6600.00, 'Tarjeta', 'Completada', 'factura_2026-08-16_13-13-00.pdf', 2, 2),
    ('2026-08-17 23:35:00', 10900.00, 'Transferencia', 'Completada', 'factura_2026-08-17_23-35-00.pdf', NULL, 3),
    ('2026-08-23 18:03:00', 3000.00, 'Efectivo', 'Completada', 'factura_2026-08-23_18-03-00.pdf', 3, 3),
    ('2026-08-24 10:20:00', 8000.00, 'Efectivo', 'Anulada', 'factura_2026-08-24_10-20-00.pdf', 4, 2);

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
DROP ROLE IF EXISTS 'rol_administrador', 'rol_cajero';
DROP USER IF EXISTS 'cm_admin'@'localhost', 'cm_cajero'@'localhost';

CREATE ROLE 'rol_administrador', 'rol_cajero';

-- Administrador: todos los permisos sobre la base codemarket
GRANT ALL PRIVILEGES ON codemarket.* TO 'rol_administrador';

-- Cajero: consulta catálogo y clientes, registra clientes y ventas, y solo
-- puede modificar la columna stock de producto. No ve empleados, no cambia
-- precios, no anula ventas y no borra nada.
GRANT SELECT ON codemarket.producto      TO 'rol_cajero';
GRANT SELECT ON codemarket.categoria     TO 'rol_cajero';
GRANT SELECT, INSERT ON codemarket.cliente       TO 'rol_cajero';
GRANT SELECT, INSERT ON codemarket.venta         TO 'rol_cajero';
GRANT SELECT, INSERT ON codemarket.detalle_venta TO 'rol_cajero';
GRANT UPDATE (stock) ON codemarket.producto      TO 'rol_cajero';

-- Usuarios de la aplicación (cambien estas contraseñas en su equipo)
CREATE USER 'cm_admin'@'localhost'  IDENTIFIED BY 'Admin_2026!';
CREATE USER 'cm_cajero'@'localhost' IDENTIFIED BY 'Cajero_2026!';

GRANT 'rol_administrador' TO 'cm_admin'@'localhost';
GRANT 'rol_cajero'        TO 'cm_cajero'@'localhost';
SET DEFAULT ROLE ALL TO 'cm_admin'@'localhost', 'cm_cajero'@'localhost';
