-- =====================================================================
-- CodeMarket - Sistema de gestión de supermercado
-- Script: esquema + datos de prueba + roles de acceso
-- Se ejecuta UNA vez como usuario root (o administrador de MySQL).
-- Usa una base NUEVA llamada "codemarket" para no tocar la vieja
-- base "supermercado".
-- =====================================================================
 
CREATE DATABASE IF NOT EXISTS codemarket
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
 
USE codemarket;
 
-- Permite volver a correr el script durante las pruebas.
-- (Borra solo tablas de "codemarket", en orden inverso por las FK.)
DROP TABLE IF EXISTS detalle_venta;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS empleados;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
 
-- =====================================================================
-- 1. TABLAS (con integridad)
-- =====================================================================
 
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(50) NOT NULL UNIQUE
);
 
CREATE TABLE productos (
    id_producto  INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20)   NOT NULL UNIQUE,
    nombre       VARCHAR(100)  NOT NULL,
    precio       DECIMAL(10,2) NOT NULL,
    stock        INT           NOT NULL DEFAULT 0,
    id_categoria INT           NOT NULL,
    CONSTRAINT chk_precio_positivo CHECK (precio > 0),
    CONSTRAINT chk_stock_no_negativo CHECK (stock >= 0),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
);
 
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    apellido   VARCHAR(60) NOT NULL,
    dni        VARCHAR(10) NOT NULL UNIQUE,
    telefono   VARCHAR(20),
    email      VARCHAR(100)
);
 
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    apellido    VARCHAR(60) NOT NULL,
    usuario     VARCHAR(30) NOT NULL UNIQUE,
    rol         ENUM('cajero', 'administrador') NOT NULL
);
 
CREATE TABLE ventas (
    id_venta    INT AUTO_INCREMENT PRIMARY KEY,
    fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_cliente  INT           NOT NULL,
    id_empleado INT           NOT NULL,
    metodo_pago ENUM('Efectivo', 'Tarjeta', 'Mercado Pago') NOT NULL,
    total       DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_total_no_negativo CHECK (total >= 0),
    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente)  REFERENCES clientes (id_cliente),
    CONSTRAINT fk_venta_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado)
);
 
-- Entidad asociativa: una venta incluye muchos productos
CREATE TABLE detalle_venta (
    id_detalle      INT AUTO_INCREMENT PRIMARY KEY,
    id_venta        INT           NOT NULL,
    id_producto     INT           NOT NULL,
    cantidad        INT           NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0),
    CONSTRAINT fk_detalle_venta
        FOREIGN KEY (id_venta)    REFERENCES ventas (id_venta),
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
);
 
-- =====================================================================
-- 2. DATOS DE PRUEBA
-- =====================================================================
 
INSERT INTO categorias (nombre) VALUES
    ('Lácteos'), ('Panadería'), ('Almacén'), ('Bebidas');
 
INSERT INTO productos (codigo, nombre, precio, stock, id_categoria) VALUES
    ('LAC-001', 'Leche entera 1L',          1200.00, 12, 1),
    ('PAN-001', 'Pan lactal',               2500.00,  7, 2),
    ('ALM-001', 'Arroz Gallo Oro 1kg',      1800.00, 39, 3),
    ('BEB-001', 'Gaseosa cola 1.5L',        3000.00, 50, 4),
    ('ALM-002', 'Cereales',                 5700.00, 46, 3),
    ('ALM-003', 'Fideos Tirabuzón 500g',    1550.00, 42, 3),
    ('LAC-002', 'Yogur natural 190g',       1200.00, 40, 1),
    ('PAN-002', 'Alfajor de chocolate',     1500.00, 39, 2),
    ('BEB-002', 'Agua mineral 500ml',       1000.00, 80, 4),
    ('LAC-003', 'Queso cremoso 500g',       5500.00, 25, 1);
 
INSERT INTO clientes (nombre, apellido, dni, telefono, email) VALUES
    ('Cliente',  'General', '00000000', NULL,         NULL),
    ('Rafael',   'Marín',   '30111222', '3511111111', 'rafael@mail.com'),
    ('Andrés',   'Oliva',   '30333444', '3512222222', 'andres@mail.com');
 
INSERT INTO empleados (nombre, apellido, usuario, rol) VALUES
    ('Gabriel', 'Roldán',  'groldan', 'administrador'),
    ('Samuel',  'Saravia', 'ssaravia', 'cajero');
 
-- Una venta de ejemplo: Cereales + Fideos + Leche = 8450
INSERT INTO ventas (fecha, id_cliente, id_empleado, metodo_pago, total)
VALUES ('2026-08-16 12:02:00', 1, 2, 'Tarjeta', 8450.00);
 
INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES
    (1, 5, 1, 5700.00),
    (1, 6, 1, 1550.00),
    (1, 1, 1, 1200.00);
 
-- =====================================================================
-- 3. ROLES DE ACCESO
-- =====================================================================
-- Un ROL es un paquete de permisos. Se lo asignamos a usuarios.
 
CREATE ROLE IF NOT EXISTS 'rol_administrador';
CREATE ROLE IF NOT EXISTS 'rol_cajero';
 
-- Administrador: puede hacer todo en la base codemarket
GRANT ALL PRIVILEGES ON codemarket.* TO 'rol_administrador';
 
-- Cajero: consulta catálogo y clientes, registra ventas y clientes,
-- y solo puede modificar la columna stock de productos.
-- NO puede ver empleados ni borrar nada.
GRANT SELECT ON codemarket.productos     TO 'rol_cajero';
GRANT SELECT ON codemarket.categorias    TO 'rol_cajero';
GRANT SELECT ON codemarket.clientes      TO 'rol_cajero';
GRANT INSERT ON codemarket.clientes      TO 'rol_cajero';
GRANT SELECT, INSERT ON codemarket.ventas         TO 'rol_cajero';
GRANT SELECT, INSERT ON codemarket.detalle_venta  TO 'rol_cajero';
GRANT UPDATE (stock) ON codemarket.productos      TO 'rol_cajero';
 
-- Usuarios de la aplicación (cambien estas contraseñas en su equipo)
CREATE USER IF NOT EXISTS 'cm_admin'@'localhost'  IDENTIFIED BY 'Admin_2026!';
CREATE USER IF NOT EXISTS 'cm_cajero'@'localhost' IDENTIFIED BY 'Cajero_2026!';
 
GRANT 'rol_administrador' TO 'cm_admin'@'localhost';
GRANT 'rol_cajero'        TO 'cm_cajero'@'localhost';
 
SET DEFAULT ROLE ALL TO 'cm_admin'@'localhost', 'cm_cajero'@'localhost';
 
-- =====================================================================
-- 4. VERIFICACIÓN RÁPIDA (opcional)
-- =====================================================================
-- SELECT p.codigo, p.nombre, p.precio, p.stock, c.nombre AS categoria
-- FROM productos p
-- INNER JOIN categorias c ON p.id_categoria = c.id_categoria;