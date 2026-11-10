import html
import re

from aroma_cafe.interfaz.web import crear_app


def abrir():
    return crear_app().test_client()


def texto(respuesta):
    pagina = re.sub(r"<[^>]+>", " ", respuesta.get_data(as_text=True))
    return " ".join(html.unescape(pagina).split())


def ver(cliente, ruta):
    return texto(cliente.get(ruta))


def vender(
    cliente, latte=0, alfajor=0, medio="efectivo", confirmado=True, empleado="Ana"
):
    datos = {
        "empleado": empleado,
        "LAT": str(latte),
        "ALF": str(alfajor),
        "medio": medio,
    }
    if confirmado:
        datos["confirmado"] = "si"
    return texto(cliente.post("/ventas", data=datos))
