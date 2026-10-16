from datetime import timedelta
from decimal import Decimal

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from tests.fabricas import HOY, leche, lote_de_leche


@pytest.fixture
def servicio() -> ServicioRecepcion:
    unidad = UnidadDeTrabajo(
        RepositorioVentas(),
        RepositorioInventario([leche()]),
        RepositorioRecepciones(),
    )
    return ServicioRecepcion(ServicioInventario(unidad), unidad)


def test_sin_recepciones_no_hay_lotes_por_devolver(servicio):
    assert servicio.lotes_por_devolver() == []


def test_solo_el_lote_rechazado_queda_por_devolver(servicio):
    servicio.registrar_recepcion(lote_de_leche(), HOY)
    rechazado = servicio.registrar_recepcion(
        lote_de_leche(numero_lote="L-102", temperatura=Decimal("25.5")), HOY
    )

    assert servicio.lotes_por_devolver() == [rechazado]


def test_el_lote_por_vencer_tambien_queda_por_devolver(servicio):
    rechazado = servicio.registrar_recepcion(
        lote_de_leche(fecha_vencimiento=HOY + timedelta(days=4)), HOY
    )

    assert servicio.lotes_por_devolver() == [rechazado]
