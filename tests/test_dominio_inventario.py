from decimal import Decimal

import pytest

from tests.fabricas import cafe


@pytest.mark.parametrize(
    "existencia, requerida, alcanza",
    [
        pytest.param(11, 10, True, id="existencia mayor"),
        pytest.param(10, 10, True, id="existencia igual: vende la última unidad"),
        pytest.param(9, 10, False, id="una unidad menos"),
        pytest.param(0, 1, False, id="sin existencia"),
    ],
)
def test_hay_disponibilidad_rn001(existencia, requerida, alcanza):
    articulo = cafe(existencia=existencia)
    assert articulo.hay_disponibilidad(Decimal(requerida)) is alcanza


def test_descontar_y_sumar_rn004():
    articulo = cafe(existencia=100)
    articulo.descontar(Decimal(18))
    assert articulo.existencia == Decimal(82)
    articulo.sumar(Decimal(500))
    assert articulo.existencia == Decimal(582)


@pytest.mark.parametrize(
    "existencia, requiere",
    [
        pytest.param(21, False, id="por encima del mínimo"),
        pytest.param(20, True, id="exactamente en el mínimo"),
        pytest.param(19, True, id="por debajo del mínimo"),
    ],
)
def test_requiere_reposicion_rn006(existencia, requiere):
    articulo = cafe(existencia=existencia, stock_minimo=20)
    assert articulo.requiere_reposicion() is requiere
