from flask import Flask, render_template, request

from aroma_cafe.dominio.ventas import ItemPedido, MedioPago, Pago, Pedido
from aroma_cafe.interfaz import consola
from aroma_cafe.interfaz.cafeteria import EMPLEADOS, PRODUCTOS, Cafeteria


def pantalla_ventas(app: Flask, cafeteria: Cafeteria) -> None:
    @app.route("/", methods=["GET", "POST"])
    @app.route("/ventas", methods=["GET", "POST"])
    def ventas() -> str:
        avisos: list[str] = []
        if request.method == "POST":
            avisos = registrar_venta(cafeteria)
        return render_template(
            "ventas.html",
            empleados=EMPLEADOS,
            productos=PRODUCTOS,
            medios=MedioPago,
            avisos=avisos,
            historial=cafeteria.ventas.historial(),
        )


def registrar_venta(cafeteria: Cafeteria) -> list[str]:
    formulario = request.form
    items: list[ItemPedido] = []
    try:
        for producto in PRODUCTOS:
            cantidad = int(formulario.get(producto.codigo) or 0)
            if cantidad != 0:
                items.append(ItemPedido(producto, cantidad))
        medio = MedioPago(formulario.get("medio"))
    except ValueError as error:
        return [f"Venta rechazada: {error}"]
    pago = Pago(medio, formulario.get("confirmado") == "si")
    empleado = formulario.get("empleado", "")
    mensaje = consola.registrar_venta(cafeteria.ventas, Pedido(items), pago, empleado)
    return [linea.strip() for linea in mensaje.splitlines()]
