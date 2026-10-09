from datetime import timedelta
from decimal import Decimal

import pytest

from aroma_cafe.dominio.excepciones import (
    DatosLoteInvalidosError,
    IdentificacionIncompletaError,
)
from aroma_cafe.dominio.inventario import UnidadMedida
from aroma_cafe.dominio.recepcion import EstadoLote
from tests.fabricas import HOY, cafe, lote_de_leche


@pytest.mark.parametrize(
    "cambios, campo",
    [
        pytest.param({"proveedor": None}, "proveedor", id="sin proveedor"),
        pytest.param({"numero_factura": None}, "numero_factura", id="sin factura"),
        pytest.param({"numero_factura": ""}, "numero_factura", id="factura vacía"),
    ],
)
def test_identificacion_incompleta_rn009(cambios, campo):
    with pytest.raises(IdentificacionIncompletaError) as rechazo:
        lote_de_leche(**cambios).validar_identificacion()
    assert rechazo.value.campo == campo


def test_identificacion_completa_rn009():
    assert lote_de_leche().validar_identificacion() is None


@pytest.mark.parametrize(
    "cambios, campo",
    [
        pytest.param({"numero_lote": ""}, "numero_lote", id="sin número de lote"),
        pytest.param({"cantidad": Decimal(0)}, "cantidad", id="cantidad 0"),
        pytest.param({"cantidad": Decimal(-1)}, "cantidad", id="cantidad negativa"),
        pytest.param({"unidad": UnidadMedida.GRAMO}, "unidad", id="unidad distinta"),
        pytest.param({"fecha_vencimiento": None}, "fecha_vencimiento", id="sin fecha"),
        pytest.param({"temperatura": None}, "temperatura", id="sin temperatura"),
    ],
)
def test_datos_invalidos_rn008(cambios, campo):
    with pytest.raises(DatosLoteInvalidosError) as rechazo:
        lote_de_leche(**cambios).validar_datos()
    assert rechazo.value.campo == campo


def test_datos_validos_con_vencimiento_y_temperatura():
    assert lote_de_leche().validar_datos() is None


def test_datos_validos_de_un_insumo_sin_vencimiento_ni_temperatura():
    lote = lote_de_leche(
        articulo=cafe(),
        unidad=UnidadMedida.GRAMO,
        fecha_vencimiento=None,
        temperatura=None,
    )
    assert lote.validar_datos() is None
    assert lote.motivo_rechazo_por_condiciones(HOY) is None


@pytest.mark.parametrize(
    "dias, temperatura, se_rechaza",
    [
        pytest.param(10, "4.0", False, id="en condiciones"),
        pytest.param(5, "4.0", False, id="límite: días iguales al mínimo"),
        pytest.param(4, "4.0", True, id="un día menos que el mínimo"),
        pytest.param(-1, "4.0", True, id="lote vencido"),
        pytest.param(10, "8", False, id="límite: temperatura igual a la máxima"),
        pytest.param(10, "8.1", True, id="una décima sobre la máxima"),
        pytest.param(10, "25.5", True, id="temperatura 25.5"),
    ],
)
def test_condiciones_del_lote_rn008(dias, temperatura, se_rechaza):
    lote = lote_de_leche(
        fecha_vencimiento=HOY + timedelta(days=dias), temperatura=Decimal(temperatura)
    )
    assert (lote.motivo_rechazo_por_condiciones(HOY) is not None) is se_rechaza


def test_la_temperatura_no_se_evalua_si_el_insumo_no_tiene_maxima():
    lote = lote_de_leche(
        articulo=cafe(), unidad=UnidadMedida.GRAMO, temperatura=Decimal("25.5")
    )
    assert lote.motivo_rechazo_por_condiciones(HOY) is None


def test_un_lote_ya_vencido_se_rechaza_aunque_el_insumo_no_exija_fecha():
    lote = lote_de_leche(
        articulo=cafe(),
        unidad=UnidadMedida.GRAMO,
        fecha_vencimiento=HOY - timedelta(days=1),
    )
    assert lote.motivo_rechazo_por_condiciones(HOY) == (
        "le quedan -1 días y el mínimo es 0"
    )


def test_el_motivo_dice_el_valor_medido_y_el_limite():
    vencido = lote_de_leche(fecha_vencimiento=HOY + timedelta(days=4))
    caliente = lote_de_leche(temperatura=Decimal("25.5"))
    assert vencido.motivo_rechazo_por_condiciones(HOY) == (
        "le quedan 4 días y el mínimo es 5"
    )
    assert caliente.motivo_rechazo_por_condiciones(HOY) == (
        "llegó a 25.5 °C y el máximo es 8 °C"
    )


def test_aceptar_y_rechazar_crean_una_copia_y_no_cambian_lo_digitado():
    digitado = lote_de_leche()
    aceptado = digitado.aceptado()
    rechazado = digitado.rechazado("llegó a 25.5 °C y el máximo es 8 °C")
    assert digitado.estado is EstadoLote.POR_REVISAR
    assert aceptado.estado is EstadoLote.ACEPTADO
    assert (rechazado.estado, rechazado.motivo_rechazo) == (
        EstadoLote.RECHAZADO,
        "llegó a 25.5 °C y el máximo es 8 °C",
    )
