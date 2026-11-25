from pathlib import Path

from flask import Flask

from aroma_cafe.datos.respaldo import Respaldo
from aroma_cafe.interfaz.cafeteria import abrir_cafeteria
from aroma_cafe.interfaz.web_inventario import pantalla_inventario
from aroma_cafe.interfaz.web_recepcion import pantalla_recepcion
from aroma_cafe.interfaz.web_ventas import pantalla_ventas

RUTA_RESPALDO = Path("respaldo") / "aroma_cafe.json"


def crear_app(respaldo: Respaldo | None = None) -> Flask:
    app = Flask(__name__, template_folder="plantillas")
    cafeteria = abrir_cafeteria(respaldo)
    pantalla_ventas(app, cafeteria)
    pantalla_inventario(app, cafeteria)
    pantalla_recepcion(app, cafeteria)
    return app


app = crear_app(Respaldo(RUTA_RESPALDO))
