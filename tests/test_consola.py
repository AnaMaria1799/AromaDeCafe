from decimal import Decimal
from unittest.mock import create_autospec

import pytest

from aroma_cafe.dominio.excepciones import (
    IdentificacionIncompletaError,
    PagoNoConfirmadoError,
    PersistenciaError,
)
from aroma_cafe.dominio.inventario import AlertaAbastecimiento
from aroma_cafe.dominio.ventas import VentaRegistrada
from aroma_cafe.interfaz import consola
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from aroma_cafe.servicios.ventas import ServicioVentas
from tests.fabricas import HOY, VENTA, lote_de_leche, pago, pedido


@pytest.fixture
def ventas():
    return create_autospec(ServicioVentas, instance=True)


@pytest.fixture
def recepcion():
    return create_autospec(ServicioRecepcion, instance=True)


def test_venta_registrada_con_alerta(ventas):
    alerta = AlertaAbastecimiento("CAF", Decimal(20), Decimal(20), VENTA.fecha_hora)
    ventas.registrar_venta.return_value = VentaRegistrada(VENTA, (alerta,))

    mensaje = consola.registrar_venta(ventas, pedido(), pago(), "Ana")

    assert mensaje == (
        "Venta registrada por $6500 en efectivo.\n"
        "  Alerta de abastecimiento: CAF quedó en 20 (stock mínimo 20)."
    )


def test_venta_rechazada_muestra_el_mensaje_de_la_regla(ventas):
    ventas.registrar_venta.side_effect = PagoNoConfirmadoError()

    mensaje = consola.registrar_venta(ventas, pedido(), pago(), "Ana")

    assert (
        mensaje == "Venta rechazada: El pago no está confirmado: la venta se cancela."
    )


def test_falla_al_guardar_la_venta_no_detiene_la_caja(ventas):
    ventas.registrar_venta.side_effect = PersistenciaError(
        "base de datos no disponible"
    )

    mensaje = consola.registrar_venta(ventas, pedido(), pago(), "Ana")

    assert mensaje == "No se pudo guardar la venta. Intente de nuevo."


def test_lote_aceptado(recepcion):
    recepcion.registrar_recepcion.return_value = lote_de_leche().aceptado()

    mensaje = consola.registrar_recepcion(recepcion, lote_de_leche(), HOY)

    assert mensaje == "Lote L-101 aceptado: entran 5000 ml de Leche."


def test_lote_rechazado_muestra_el_motivo(recepcion):
    recepcion.registrar_recepcion.return_value = lote_de_leche().rechazado(
        "llegó a 25.5 °C y el máximo es 8 °C"
    )

    mensaje = consola.registrar_recepcion(recepcion, lote_de_leche(), HOY)

    assert mensaje == "Lote L-101 rechazado: llegó a 25.5 °C y el máximo es 8 °C."


def test_recepcion_no_registrada_muestra_el_campo(recepcion):
    recepcion.registrar_recepcion.side_effect = IdentificacionIncompletaError(
        "proveedor"
    )

    mensaje = consola.registrar_recepcion(recepcion, lote_de_leche(), HOY)

    assert mensaje == (
        "Recepción no registrada: "
        "Falta el dato obligatorio 'proveedor' de la recepción."
    )


def test_falla_al_guardar_la_recepcion_no_detiene_la_operacion(recepcion):
    recepcion.registrar_recepcion.side_effect = PersistenciaError("sin conexión")

    mensaje = consola.registrar_recepcion(recepcion, lote_de_leche(), HOY)

    assert mensaje == "No se pudo guardar la recepción. Intente de nuevo."
