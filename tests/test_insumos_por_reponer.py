import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.servicios.inventario import ServicioInventario
from tests.fabricas import cafe, leche


def inventario_con(*articulos):
    unidad = UnidadDeTrabajo(
        RepositorioVentas(),
        RepositorioInventario(articulos),
        RepositorioRecepciones(),
    )
    return ServicioInventario(unidad)


def test_si_todo_esta_sobre_el_minimo_no_hay_nada_por_reponer():
    inventario = inventario_con(cafe(existencia=100, stock_minimo=20), leche())

    assert inventario.insumos_por_reponer() == []


@pytest.mark.parametrize(
    "existencia, por_reponer",
    [
        pytest.param(21, [], id="uno sobre el minimo"),
        pytest.param(20, ["CAF"], id="justo en el minimo"),
        pytest.param(19, ["CAF"], id="uno debajo del minimo"),
    ],
)
def test_limites_del_stock_minimo_rn006(existencia, por_reponer):
    inventario = inventario_con(cafe(existencia=existencia, stock_minimo=20), leche())

    assert inventario.insumos_por_reponer() == por_reponer


def test_solo_aparecen_los_insumos_que_hay_que_reponer():
    inventario = inventario_con(
        cafe(existencia=196, stock_minimo=200), leche(existencia=6400)
    )

    assert inventario.insumos_por_reponer() == ["CAF"]
