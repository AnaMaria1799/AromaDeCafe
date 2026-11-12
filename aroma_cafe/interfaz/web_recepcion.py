from datetime import date
from decimal import Decimal

from flask import Flask, render_template, request

from aroma_cafe.dominio.inventario import UnidadMedida
from aroma_cafe.dominio.recepcion import LoteRecepcion, Proveedor
from aroma_cafe.interfaz import consola
from aroma_cafe.interfaz.cafeteria import EMPLEADOS, Cafeteria

NOMBRES_DE_CAMPOS = {
    "'proveedor'": '"Proveedor"',
    "'numero_factura'": '"Número de factura"',
    "'numero_lote'": '"Número de lote"',
    "'cantidad'": '"Cantidad"',
    "'unidad'": '"Unidad"',
    "'fecha_vencimiento'": '"Fecha de vencimiento"',
    "'temperatura'": '"Temperatura"',
}


def pantalla_recepcion(app: Flask, cafeteria: Cafeteria) -> None:
    @app.route("/recepcion", methods=["GET", "POST"])
    def recepcion() -> str:
        mensaje = ""
        if request.method == "POST":
            mensaje = registrar_recepcion(cafeteria)
        return render_template(
            "recepcion.html",
            articulos=cafeteria.inventario_repo.listar(),
            unidades=UnidadMedida,
            empleados=EMPLEADOS,
            mensaje=mensaje,
            devoluciones=cafeteria.recepcion.lotes_por_devolver(),
        )


def registrar_recepcion(cafeteria: Cafeteria) -> str:
    lote = leer_lote(cafeteria)
    mensaje = consola.registrar_recepcion(cafeteria.recepcion, lote, date.today())
    for campo, nombre in NOMBRES_DE_CAMPOS.items():
        mensaje = mensaje.replace(campo, nombre)
    return mensaje


def leer_lote(cafeteria: Cafeteria) -> LoteRecepcion:
    formulario = request.form
    nit = formulario.get("nit", "")
    proveedor = formulario.get("proveedor", "")
    vencimiento = formulario.get("vencimiento", "")
    temperatura = formulario.get("temperatura", "")
    return LoteRecepcion(
        numero_lote=formulario.get("lote", ""),
        articulo=cafeteria.inventario_repo.obtener(formulario.get("insumo", "")),
        cantidad=Decimal(formulario.get("cantidad") or 0),
        unidad=UnidadMedida(formulario.get("unidad")),
        responsable=formulario.get("responsable", ""),
        proveedor=Proveedor(nit, proveedor) if nit and proveedor else None,
        numero_factura=formulario.get("factura", ""),
        fecha_vencimiento=date.fromisoformat(vencimiento) if vencimiento else None,
        temperatura=Decimal(temperatura) if temperatura else None,
    )
