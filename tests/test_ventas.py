from decimal import Decimal
from unittest.mock import patch

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import (
    ExistenciaInsuficienteError,
    MedioPagoNoHabilitadoError,
    PagoNoConfirmadoError,
    PedidoVacioError,
    PersistenciaError,
)
from aroma_cafe.dominio.ventas import ItemPedido, MedioPago
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.ventas import ServicioVentas
from tests.fabricas import LATTE, TINTO, cafe, cargar_existencias, leche, pago, pedido


@pytest.fixture
def servicio(inventario, unidad) -> ServicioVentas:
    return ServicioVentas(inventario, unidad)


def afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo):
    ventas_repo.guardar.assert_not_called()
    inventario_repo.guardar.assert_not_called()
    inventario_repo.registrar_movimiento.assert_not_called()
    ventas_repo.confirmar.assert_not_called()


def test_c1_pedido_sin_productos(servicio, ventas_repo, inventario_repo):
    with pytest.raises(PedidoVacioError):
        servicio.registrar_venta(pedido(), pago(), "Ana")

    inventario_repo.obtener.assert_not_called()
    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_c2_el_primer_consumo_no_alcanza(servicio, ventas_repo, inventario_repo):
    cargar_existencias(inventario_repo, cafe(existencia=17), leche(existencia=1000))

    with pytest.raises(ExistenciaInsuficienteError) as rechazo:
        servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    assert rechazo.value.codigo_articulo == "CAF"
    inventario_repo.obtener.assert_called_once_with("CAF")
    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_c3_el_segundo_consumo_no_alcanza(servicio, ventas_repo, inventario_repo):
    cargar_existencias(inventario_repo, cafe(existencia=18), leche(existencia=199))

    with pytest.raises(ExistenciaInsuficienteError) as rechazo:
        servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    assert (rechazo.value.codigo_articulo, rechazo.value.requerida) == (
        "LEC",
        Decimal(200),
    )
    assert inventario_repo.obtener.call_count == 2
    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_c4_medio_de_pago_no_habilitado(
    inventario, unidad, ventas_repo, inventario_repo
):
    solo_efectivo_y_transferencia = frozenset(
        {MedioPago.EFECTIVO, MedioPago.TRANSFERENCIA}
    )
    servicio = ServicioVentas(inventario, unidad, solo_efectivo_y_transferencia)
    cargar_existencias(inventario_repo, cafe(), leche())

    with pytest.raises(MedioPagoNoHabilitadoError) as rechazo:
        servicio.registrar_venta(
            pedido(ItemPedido(LATTE, 1)), pago(MedioPago.TARJETA), "Ana"
        )

    assert rechazo.value.medio == "tarjeta"
    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_c5_pago_no_confirmado(servicio, ventas_repo, inventario_repo):
    cargar_existencias(inventario_repo, cafe(), leche())

    with pytest.raises(PagoNoConfirmadoError):
        servicio.registrar_venta(
            pedido(ItemPedido(LATTE, 1)), pago(confirmado=False), "Ana"
        )

    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_c6_si_falla_el_guardado_se_revierte_todo(
    servicio, ventas_repo, inventario_repo, recepciones_repo
):
    cargar_existencias(inventario_repo, cafe(), leche())
    ventas_repo.guardar.side_effect = PersistenciaError("base de datos no disponible")

    with pytest.raises(PersistenciaError):
        servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    ventas_repo.revertir.assert_called_once_with()
    inventario_repo.revertir.assert_called_once_with()
    recepciones_repo.revertir.assert_called_once_with()
    ventas_repo.confirmar.assert_not_called()
    inventario_repo.confirmar.assert_not_called()


def test_c7_venta_valida_se_guarda_y_descuenta(
    servicio, ventas_repo, inventario_repo, recepciones_repo
):
    grano, lacteo = cafe(existencia=100, stock_minimo=20), leche(existencia=1000)
    cargar_existencias(inventario_repo, grano, lacteo)
    items = [ItemPedido(LATTE, 2)]

    registro = servicio.registrar_venta(pedido(*items), pago(MedioPago.TARJETA), "Ana")

    venta = registro.venta
    assert (venta.empleado, venta.items, venta.valor_total, venta.medio_pago) == (
        "Ana",
        tuple(items),
        Decimal(13000),
        MedioPago.TARJETA,
    )
    assert registro.alertas == ()
    assert (grano.existencia, lacteo.existencia) == (Decimal(64), Decimal(600))
    ventas_repo.guardar.assert_called_once_with(venta)
    assert inventario_repo.registrar_movimiento.call_count == 2
    ventas_repo.confirmar.assert_called_once_with()
    inventario_repo.confirmar.assert_called_once_with()
    recepciones_repo.confirmar.assert_called_once_with()
    ventas_repo.revertir.assert_not_called()


def test_la_venta_entrega_las_alertas_de_abastecimiento(servicio, inventario_repo):
    cargar_existencias(inventario_repo, cafe(existencia=38, stock_minimo=20), leche())

    registro = servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    assert [(a.codigo_articulo, a.existencia) for a in registro.alertas] == [
        ("CAF", Decimal(20))
    ]


def test_dos_productos_con_el_mismo_insumo_se_suman_antes_de_comparar(
    servicio, ventas_repo, inventario_repo
):
    cargar_existencias(inventario_repo, cafe(existencia=27), leche())
    latte_y_tinto = pedido(ItemPedido(LATTE, 1), ItemPedido(TINTO, 1))

    with pytest.raises(ExistenciaInsuficienteError) as rechazo:
        servicio.registrar_venta(latte_y_tinto, pago(), "Ana")

    assert (rechazo.value.existencia, rechazo.value.requerida) == (
        Decimal(27),
        Decimal(28),
    )
    afirmar_que_no_se_guardo_nada(ventas_repo, inventario_repo)


def test_si_otra_venta_consumio_la_existencia_se_revierte_tambien_la_venta(
    servicio, ventas_repo, inventario_repo
):
    al_verificar, al_descontar = cafe(existencia=10), cafe(existencia=9)
    inventario_repo.obtener.side_effect = [al_verificar, al_descontar]

    with pytest.raises(ExistenciaInsuficienteError):
        servicio.registrar_venta(pedido(ItemPedido(TINTO, 1)), pago(), "Ana")

    ventas_repo.guardar.assert_called_once()
    ventas_repo.revertir.assert_called_once_with()
    inventario_repo.revertir.assert_called_once_with()
    ventas_repo.confirmar.assert_not_called()
    inventario_repo.guardar.assert_not_called()


def test_si_falla_el_descuento_del_segundo_insumo_no_queda_nada_a_medias():
    inventario_repo = RepositorioInventario(
        [cafe(existencia=100), leche(existencia=1000)]
    )
    unidad = UnidadDeTrabajo(
        RepositorioVentas(), inventario_repo, RepositorioRecepciones()
    )
    servicio = ServicioVentas(ServicioInventario(unidad), unidad)
    guardar_real = inventario_repo.guardar

    def guardar_que_falla_con_la_leche(articulo):
        if articulo.codigo == "LEC":
            raise PersistenciaError("base de datos no disponible")
        guardar_real(articulo)

    falla = patch.object(inventario_repo, "guardar", guardar_que_falla_con_la_leche)
    with falla, pytest.raises(PersistenciaError):
        servicio.registrar_venta(pedido(ItemPedido(LATTE, 1)), pago(), "Ana")

    assert unidad.ventas.listar() == []
    assert inventario_repo.obtener("CAF").existencia == Decimal(100)
    assert inventario_repo.movimientos() == []

    servicio.registrar_venta(pedido(ItemPedido(TINTO, 1)), pago(), "Ana")

    assert len(unidad.ventas.listar()) == 1
    assert inventario_repo.obtener("CAF").existencia == Decimal(90)
    assert len(inventario_repo.movimientos()) == 1


@pytest.mark.parametrize("sin_inventario, sin_unidad", [(True, False), (False, True)])
def test_no_se_puede_crear_el_servicio_con_dependencias_nulas(
    inventario, unidad, sin_inventario, sin_unidad
):
    with pytest.raises(ValueError, match="ServicioVentas necesita"):
        ServicioVentas(
            None if sin_inventario else inventario, None if sin_unidad else unidad
        )
