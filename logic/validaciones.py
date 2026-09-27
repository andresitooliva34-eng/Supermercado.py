def limpiar_dni(texto):
    return texto.replace(".", "").replace(" ", "").strip()


def dni_valido(dni):
    return dni == "" or (dni.isdigit() and 7 <= len(dni) <= 8)


def telefono_valido(telefono):
    permitidos = "0123456789 +-()" 
    return all(caracter in permitidos for caracter in telefono) 
