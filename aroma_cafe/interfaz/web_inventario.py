from flask import Flask, render_template

from aroma_cafe.interfaz.cafeteria import Cafeteria


def pantalla_inventario(app: Flask, cafeteria: Cafeteria) -> None:
    @app.route("/inventario")
    def inventario() -> str:
        articulos = cafeteria.inventario_repo.listar()
        codigos = cafeteria.inventario.insumos_por_reponer()
        por_reponer = [a.nombre for a in articulos if a.codigo in codigos]
        return render_template(
            "inventario.html", articulos=articulos, por_reponer=por_reponer
        )
