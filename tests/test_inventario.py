from decimal import Decimal

import pytest

from aroma_cafe.dominio.excepciones import ExistenciaInsuficienteError
from aroma_cafe.dominio.movimientos import SalidaInventario
from aroma_cafe.servicios.inventario import ServicioInventario
from tests.fabricas import VENTA, cafe, cargar_existencias, leche


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


def test_c1_sin_consumos_no_descuenta_ni_registra(inventario, inventario_repo):
    alertas = inventario.descontar_por_venta(VENTA, {})

    assert alertas == []
    inventario_repo.obtener.assert_not_called()
    inventario_repo.guardar.assert_not_called()
    inventario_repo.registrar_movimiento.assert_not_called()


def test_c2_descuenta_y_registra_la_salida_sin_alerta(inventario, inventario_repo):
    articulo = cafe(existencia=100, stock_minimo=20)
    cargar_existencias(inventario_repo, articulo)

    alertas = inventario.descontar_por_venta(VENTA, {"CAF": Decimal(18)})

    assert articulo.existencia == Decimal(82)
    assert alertas == []
    inventario_repo.guardar.assert_called_once_with(articulo)
    inventario_repo.registrar_movimiento.assert_called_once_with(
        SalidaInventario(VENTA.fecha_hora, "CAF", Decimal(18), "Ana", VENTA)
    )


@pytest.mark.parametrize(
    "existencia, queda, hay_alerta",
    [
        pytest.param(39, 21, False, id="queda por encima del mínimo"),
        pytest.param(38, 20, True, id="c3: queda exactamente en el mínimo"),
        pytest.param(37, 19, True, id="c3: queda por debajo del mínimo"),
    ],
)
def test_c3_alerta_si_queda_en_el_stock_minimo_o_por_debajo(
    inventario, inventario_repo, existencia, queda, hay_alerta
):
    cargar_existencias(inventario_repo, cafe(existencia=existencia, stock_minimo=20))

    alertas = inventario.descontar_por_venta(VENTA, {"CAF": Decimal(18)})

    assert [(a.codigo_articulo, a.existencia, a.stock_minimo) for a in alertas] == (
        [("CAF", Decimal(queda), Decimal(20))] if hay_alerta else []
    )


def test_c4_si_ya_no_alcanza_lanza_error_y_no_escribe(inventario, inventario_repo):
    cargar_existencias(inventario_repo, cafe(existencia=0))

    with pytest.raises(ExistenciaInsuficienteError) as rechazo:
        inventario.descontar_por_venta(VENTA, {"CAF": Decimal(1)})

    assert (rechazo.value.existencia, rechazo.value.requerida) == (
        Decimal(0),
        Decimal(1),
    )
    inventario_repo.guardar.assert_not_called()
    inventario_repo.registrar_movimiento.assert_not_called()


def test_descontar_exactamente_la_existencia_la_deja_en_cero(
    inventario, inventario_repo
):
    articulo = cafe(existencia=1, stock_minimo=0)
    cargar_existencias(inventario_repo, articulo)

    alertas = inventario.descontar_por_venta(VENTA, {"CAF": Decimal(1)})

    assert articulo.existencia == Decimal(0)
    assert len(alertas) == 1


def test_el_bucle_descuenta_cada_consumo_del_pedido(inventario, inventario_repo):
    grano, lacteo = cafe(existencia=100), leche(existencia=1000)
    cargar_existencias(inventario_repo, grano, lacteo)

    inventario.descontar_por_venta(VENTA, {"CAF": Decimal(18), "LEC": Decimal(200)})

    assert (grano.existencia, lacteo.existencia) == (Decimal(82), Decimal(800))
    assert inventario_repo.registrar_movimiento.call_count == 2
