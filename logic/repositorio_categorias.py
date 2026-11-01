from logic.repositorio_base_mysql import RepositorioMySQLBase


class RepositorioCategoriasMySQL(RepositorioMySQLBase):
    """Persistencia de categorías."""

    def listar_categorias(self):
        return [
            {"id": fila[0], "nombre": fila[1]}
            for fila in self._consultar(
                "SELECT id_categoria, nombre FROM categorias ORDER BY nombre"
            )
        ]

    def guardar_categoria(self, categoria):
        nombre = categoria["nombre"].strip()
        if categoria.get("id"):
            self._ejecutar(
                "UPDATE categorias SET nombre = %s WHERE id_categoria = %s",
                (nombre, categoria["id"]),
                administrativa=True
            )
            return categoria["id"]
        return self._ejecutar(
            "INSERT INTO categorias (nombre) VALUES (%s)",
            (nombre,),
            administrativa=True
        )

    def eliminar_categoria(self, id_categoria):
        self._ejecutar(
            "DELETE FROM categorias WHERE id_categoria = %s",
            (id_categoria,),
            administrativa=True
        )
