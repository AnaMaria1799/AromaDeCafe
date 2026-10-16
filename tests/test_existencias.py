from decimal import Decimal

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import PersistenciaError
from aroma_cafe.servicios.inventario import ServicioInventario
from tests.fabricas import VENTA, cafe, leche


@pytest.fixture
def unidad_real() -> UnidadDeTrabajo:
    return UnidadDeTrabajo(
        RepositorioVentas(),
        RepositorioInventario([cafe(existencia=100), leche(existencia=1000)]),
        RepositorioRecepciones(),
    )


def test_muestra_cuanto_queda_de_cada_insumo(unidad_real):
    inventario = ServicioInventario(unidad_real)

    assert inventario.existencias() == {
        "CAF": Decimal(100),
        "LEC": Decimal(1000),
    }


def test_despues_de_una_venta_se_ve_la_existencia_actualizada(unidad_real):
    inventario = ServicioInventario(unidad_real)

    with unidad_real:
        inventario.descontar_por_venta(VENTA, {"CAF": Decimal(18), "LEC": Decimal(200)})

    assert inventario.existencias() == {
        "CAF": Decimal(82),
        "LEC": Decimal(800),
    }


def test_si_la_venta_se_revierte_las_existencias_no_cambian(unidad_real):
    inventario = ServicioInventario(unidad_real)

    with pytest.raises(PersistenciaError), unidad_real:
        inventario.descontar_por_venta(VENTA, {"CAF": Decimal(18)})
        raise PersistenciaError("base de datos no disponible")

    assert inventario.existencias() == {
        "CAF": Decimal(100),
        "LEC": Decimal(1000),
    }
