from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def exportar_carrito_pdf(carrito):
    carpeta_facturas = Path("data/facturas")
    carpeta_facturas.mkdir(parents=True, exist_ok=True)

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ruta_pdf = carpeta_facturas / f"factura_{fecha}.pdf"

    documento = SimpleDocTemplate(str(ruta_pdf), pagesize=A4)
    estilos = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("Comprobante de compra", estilos["Title"]))
    contenido.append(Spacer(1, 20))

    datos_tabla = [
        ["Producto", "Cantidad", "Precio", "Subtotal"]
    ]

    for item in carrito.items:
        producto = item["producto"]
        cantidad = item["cantidad"]
        subtotal = producto.precio * cantidad

        datos_tabla.append([
            producto.nombre,
            str(cantidad),
            f"${producto.precio}",
            f"${subtotal}"
        ])

    datos_tabla.append([
        "",
        "",
        "TOTAL",
        f"${carrito.calcular_total()}"
    ])

    tabla = Table(datos_tabla)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.green),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey)
    ]))

    contenido.append(tabla)
    documento.build(contenido)

    return ruta_pdf