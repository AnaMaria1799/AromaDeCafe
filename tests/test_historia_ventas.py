import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import PagoNoConfirmadoError
from aroma_cafe.dominio.ventas import ItemPedido
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.ventas import ServicioVentas
from tests.fabricas import LATTE, cafe, leche, pago, pedido


@pytest.fixture
def servicio() -> ServicioVentas:
    unidad = UnidadDeTrabajo(
        RepositorioVentas(),
        RepositorioInventario([cafe(), leche()]),
        RepositorioRecepciones(),
    )
    return ServicioVentas(ServicioInventario(unidad), unidad)


def test_el_historial_empieza_vacio(servicio):
    assert servicio.historial() == []


def test_la_venta_registrada_queda_en_el_historial(servicio):
    registro = servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    assert servicio.historial() == [registro.venta]


def test_la_venta_rechazada_no_queda_en_el_historial(servicio):
    with pytest.raises(PagoNoConfirmadoError):
        servicio.registrar_venta(
            pedido(ItemPedido(LATTE, 1)), pago(confirmado=False), "Ana"
        )

    assert servicio.historial() == []
