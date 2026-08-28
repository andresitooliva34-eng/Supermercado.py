from logic.carrito import Carrito
from logic.producto import Producto
from logic.supermercado import Supermercado


def mostrar_resultados(productos):
    if not productos:
        print("No se encontraron productos.")
        return

    for producto in productos:
        print(producto)


def pedir_entero(mensaje):
    try:
        return int(input(mensaje))
    except ValueError:
        print("Debes ingresar un número.")
        return None


def main():
    supermercado = Supermercado()
    supermercado.cargar_productos()

    carrito = Carrito()

    while True:
        print("\n--- SUPERMERCADO ---")
        print("1. Ver productos")
        print("2. Buscar por nombre")
        print("3. Buscar por categoría")
        print("4. Agregar producto al carrito")
        print("5. Modificar cantidad del carrito")
        print("6. Eliminar producto del carrito")
        print("7. Ver carrito")
        print("8. Finalizar compra")
        print("9. Agregar producto al supermercado")
        print("0. Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            supermercado.listar_productos()

        elif opcion == "2":
            texto = input("Escribe el nombre a buscar: ")
            resultados = supermercado.buscar_por_nombre(texto)
            mostrar_resultados(resultados)

        elif opcion == "3":
            categoria = input("Escribe la categoría: ")
            resultados = supermercado.buscar_por_categoria(categoria)
            mostrar_resultados(resultados)

        elif opcion == "4":
            id_producto = pedir_entero("ID del producto: ")
            cantidad = pedir_entero("Cantidad: ")

            if id_producto is not None and cantidad is not None:
                producto = supermercado.buscar_por_id(id_producto)

                if producto is None:
                    print("No existe un producto con ese ID.")

                elif carrito.agregar_producto(producto, cantidad):
                    print("Producto agregado al carrito.")

                else:
                    print("No hay suficiente stock.")

        elif opcion == "5":
            id_producto = pedir_entero("ID del producto: ")
            cantidad = pedir_entero("Nueva cantidad: ")

            if id_producto is not None and cantidad is not None:
                if carrito.modificar_cantidad(id_producto, cantidad):
                    print("Cantidad actualizada.")
                else:
                    print("No se pudo modificar el producto.")

        elif opcion == "6":
            id_producto = pedir_entero("ID del producto a eliminar: ")

            if id_producto is not None:
                if carrito.eliminar_producto(id_producto):
                    print("Producto eliminado.")
                else:
                    print("El producto no está en el carrito.")

        elif opcion == "7":
            carrito.mostrar_carrito()

        elif opcion == "8":
            if not carrito.items:
                print("El carrito está vacío.")

            else:
                carrito.mostrar_carrito()
                confirmar = input("¿Confirmar compra? (s/n): ").lower()

                if confirmar == "s":
                    for item in carrito.items:
                        producto = item["producto"]
                        cantidad = item["cantidad"]
                        producto.descontar_stock(cantidad)

                    carrito.vaciar_carrito()
                    print("¡Compra realizada con éxito!")

        elif opcion == "9":
            nombre = input("Nombre: ")
            categoria = input("Categoría: ")
            precio = pedir_entero("Precio: ")
            stock = pedir_entero("Stock: ")

            if precio is not None and stock is not None:
                nuevo_id = len(supermercado.productos) + 1

                nuevo_producto = Producto(
                    nuevo_id,
                    nombre,
                    categoria,
                    precio,
                    stock
                )

                supermercado.agregar_producto(nuevo_producto)
                print("Producto agregado al supermercado.")

        elif opcion == "0":
            print("¡Hasta luego!")
            break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()