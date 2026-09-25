# 🛒 Supermercado — Sistema de Gestión

## 📌 Descripción

Aplicación de escritorio desarrollada en Python y Tkinter para la gestión interna de un supermercado.

El sistema está orientado principalmente a **cajeros y administradores**, permitiendo gestionar productos, categorías, empleados, clientes y ventas.

## 🚀 Funcionalidades

- 🔐 Inicio de sesión de empleados.
- 👥 Gestión de roles y permisos.
- 📦 ABM de productos.
- 🗂️ ABM de categorías.
- 👨‍💼 ABM de empleados.
- 👤 Gestión de clientes.
- 🛒 Carrito de compras.
- 💰 Registro de ventas.
- 📊 Control de stock.
- 📋 Historial de ventas.
- 📄 Exportación de información a PDF.
- 📊 Exportación de información a Excel.
- 💾 Persistencia de datos mediante archivos JSON.

## 👥 Roles del sistema

El sistema contempla los siguientes roles:

- Administrador
- Gerente
- Supervisor
- Cajero
- Repositor
- Vendedor

Los permisos disponibles dependen del rol del empleado.

## 🔑 Acceso inicial

Para realizar la primera prueba del sistema se puede utilizar:

**Usuario:** `admin`

**Contraseña:** `admin123`

El sistema permite posteriormente gestionar los empleados desde el módulo correspondiente.

## 🛠️ Tecnologías utilizadas

- Python
- Tkinter
- JSON
- ReportLab
- OpenPyXL
- Git / GitHub

## 📂 Estructura del proyecto

```text
Supermercado.py/
│
├── main.py
├── gui/
├── logic/
├── data/
├── assets/
├── README.md
└── requirements.txt