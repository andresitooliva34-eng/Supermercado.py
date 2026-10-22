-- Habilita la cuenta de prueba que muestra la ventana de inicio de sesión.
-- Usuario: admin | Contraseña: admin123
-- Ejecutar una vez en una base existente de CodeMarket.
-- No cambia la contraseña si ya existe el usuario "admin".
USE codemarket;

INSERT IGNORE INTO empleados
    (nombre, apellido, usuario, rol, clave, activo)
VALUES
    ('Administrador', 'Demo', 'admin', 'administrador',
     '$2b$12$CekHAIBrmdsVtmkqMRwGp.eUlvw/e5J6BPZNCAmky1UVPo0iULqbu', 1);
