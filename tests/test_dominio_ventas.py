from decimal import Decimal

import pytest

from aroma_cafe.dominio.ventas import ItemPedido, LineaReceta, MedioPago, Pago, Producto
from tests.fabricas import LATTE, TINTO, pedido


def test_pedido_vacio():
    assert pedido().esta_vacio()
    assert not pedido(ItemPedido(TINTO, 1)).esta_vacio()


def test_consumos_multiplica_la_receta_por_la_cantidad():
    assert pedido(ItemPedido(LATTE, 2)).consumos() == {
        "CAF": Decimal(36),
        "LEC": Decimal(400),
    }


def test_consumos_suma_los_productos_que_comparten_insumo():
    consumos = pedido(ItemPedido(LATTE, 1), ItemPedido(TINTO, 1)).consumos()
    assert consumos == {"CAF": Decimal(28), "LEC": Decimal(200)}


def test_valor_total():
    assert pedido(ItemPedido(LATTE, 2), ItemPedido(TINTO, 1)).valor_total() == 16000


@pytest.mark.parametrize("cantidad", [0, -1])
def test_un_item_sin_cantidad_positiva_no_se_puede_construir(cantidad):
    with pytest.raises(ValueError, match="mayor que cero"):
        ItemPedido(LATTE, cantidad)


def test_un_producto_sin_receta_no_se_puede_construir():
    with pytest.raises(ValueError, match="línea de receta"):
        Producto("AGU", "Agua", Decimal(2500), ())


@pytest.mark.parametrize("cantidad", [0, -1])
def test_una_linea_de_receta_sin_cantidad_positiva_no_se_puede_construir(cantidad):
    with pytest.raises(ValueError, match="mayor que cero"):
        LineaReceta("CAF", Decimal(cantidad))


def test_un_pago_sin_medio_no_se_puede_construir():
    with pytest.raises(ValueError, match="medio de pago"):
        Pago(None, confirmado=True)


def test_un_pago_valido_conserva_sus_datos():
    pago = Pago(MedioPago.TARJETA, confirmado=False)
    assert (pago.medio, pago.confirmado) == (MedioPago.TARJETA, False)
