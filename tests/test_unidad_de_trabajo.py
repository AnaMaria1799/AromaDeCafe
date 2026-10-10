from decimal import Decimal

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import PersistenciaError
from tests.fabricas import VENTA, cafe, lote_de_leche


@pytest.fixture
def unidad() -> UnidadDeTrabajo:
    return UnidadDeTrabajo(
        RepositorioVentas(),
        RepositorioInventario([cafe(existencia=100)]),
        RepositorioRecepciones(),
    )


def escribir_en_los_tres_repositorios(unidad: UnidadDeTrabajo) -> None:
    unidad.ventas.guardar(VENTA)
    unidad.inventario.guardar(cafe(existencia=82))
    unidad.recepciones.guardar(lote_de_leche())


def test_al_salir_sin_error_confirma_los_tres_repositorios(unidad):
    with unidad:
        escribir_en_los_tres_repositorios(unidad)

    assert unidad.ventas.listar() == [VENTA]
    assert unidad.inventario.obtener("CAF").existencia == Decimal(82)
    assert unidad.recepciones.existe("FE-2301", "L-101")


def test_si_hay_una_excepcion_revierte_los_tres_repositorios(unidad):
    with pytest.raises(PersistenciaError), unidad:
        escribir_en_los_tres_repositorios(unidad)
        raise PersistenciaError("base de datos no disponible")

    assert unidad.ventas.listar() == []
    assert unidad.inventario.obtener("CAF").existencia == Decimal(100)
    assert not unidad.recepciones.existe("FE-2301", "L-101")


def test_lo_revertido_no_se_guarda_en_la_operacion_siguiente(unidad):
    with pytest.raises(PersistenciaError), unidad:
        escribir_en_los_tres_repositorios(unidad)
        raise PersistenciaError("base de datos no disponible")
    with unidad:
        unidad.inventario.guardar(cafe(existencia=90))

    assert unidad.ventas.listar() == []
    assert unidad.inventario.obtener("CAF").existencia == Decimal(90)
