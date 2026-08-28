from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle
)


def exportar_carrito_pdf(carrito):
    # Crea la carpeta donde se guardarán las facturas
    carpeta_facturas = Path("data/facturas")
    carpeta_facturas.mkdir(
        parents=True,
        exist_ok=True
    )

    # Genera un nombre único utilizando la fecha y hora actual
    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    ruta_pdf = (
        carpeta_facturas /
        f"factura_{fecha}.pdf"
    )

    # Crea el documento PDF
    documento = SimpleDocTemplate(
        str(ruta_pdf),
        pagesize=A4
    )

    estilos = getSampleStyleSheet()

    contenido = []

    # Agrega el título del comprobante
    contenido.append(
        Paragraph(
            "Comprobante de compra",
            estilos["Title"]
        )
    )

    contenido.append(
        Spacer(1, 20)
    )

    # Encabezados de la tabla
    datos_tabla = [
        ["Producto", "Cantidad", "Precio", "Subtotal"]
    ]

    # Agrega cada producto del carrito a la factura
    for item in carrito.items:
        producto = item["producto"]
        cantidad = item["cantidad"]

        # Calcula el subtotal de cada producto
        subtotal = producto.precio * cantidad

        datos_tabla.append([
            producto.nombre,
            str(cantidad),
            f"${producto.precio}",
            f"${subtotal}"
        ])

    # Agrega el total de la compra al final
    datos_tabla.append([
        "",
        "",
        "TOTAL",
        f"${carrito.calcular_total()}"
    ])

    # Crea y aplica formato a la tabla
    tabla = Table(datos_tabla)

    tabla.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.green),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey)
        ])
    )

    contenido.append(tabla)

    # Genera y guarda el archivo PDF
    documento.build(contenido)

    # Devuelve la ubicación del archivo generado
    return ruta_pdf