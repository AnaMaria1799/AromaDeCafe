from decimal import Decimal

import pytest

from aroma_cafe.dominio.excepciones import ExistenciaInsuficienteError
from aroma_cafe.servicios.inventario import ServicioInventario
from tests.fabricas import cafe, cargar_existencias


def test_no_se_puede_crear_el_servicio_sin_unidad_de_trabajo():
    with pytest.raises(ValueError, match="unidad de trabajo"):
        ServicioInventario(None)


@pytest.mark.parametrize(
    "existencia, alcanza",
    [
        pytest.param(11, True, id="existencia mayor"),
        pytest.param(10, True, id="existencia igual: vende la última unidad"),
        pytest.param(9, False, id="una unidad menos"),
    ],
)
def test_verificar_disponibilidad_en_el_limite(
    inventario, inventario_repo, existencia, alcanza
):
    cargar_existencias(inventario_repo, cafe(existencia=existencia))

    if alcanza:
        assert inventario.verificar_disponibilidad({"CAF": Decimal(10)}) is None
    else:
        with pytest.raises(ExistenciaInsuficienteError):
            inventario.verificar_disponibilidad({"CAF": Decimal(10)})

    inventario_repo.guardar.assert_not_called()


def test_verificar_sin_consumos_no_consulta_el_inventario(inventario, inventario_repo):
    assert inventario.verificar_disponibilidad({}) is None
    inventario_repo.obtener.assert_not_called()
