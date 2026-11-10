from flask import Flask

from aroma_cafe.interfaz.cafeteria import abrir_cafeteria
from aroma_cafe.interfaz.web_ventas import pantalla_ventas


def crear_app() -> Flask:
    app = Flask(__name__, template_folder="plantillas")
    cafeteria = abrir_cafeteria()
    pantalla_ventas(app, cafeteria)
    return app


app = crear_app()
