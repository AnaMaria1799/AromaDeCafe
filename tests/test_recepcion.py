from datetime import timedelta
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
    DatosLoteInvalidosError,
    IdentificacionIncompletaError,
    PersistenciaError,
)
from aroma_cafe.dominio.movimientos import EntradaInventario
from aroma_cafe.dominio.recepcion import EstadoLote
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from tests.fabricas import HOY, cargar_existencias, leche, lote_de_leche


@pytest.fixture
def servicio(inventario, unidad) -> ServicioRecepcion:
    return ServicioRecepcion(inventario, unidad)


def afirmar_que_no_se_guardo_nada(recepciones_repo, inventario_repo):
    recepciones_repo.guardar.assert_not_called()
    inventario_repo.guardar.assert_not_called()
    inventario_repo.registrar_movimiento.assert_not_called()
    recepciones_repo.confirmar.assert_not_called()


@pytest.mark.parametrize(
    "cambios, campo",
    [
        pytest.param({"proveedor": None}, "proveedor", id="sin proveedor"),
        pytest.param({"numero_factura": None}, "numero_factura", id="sin factura"),
    ],
)
def test_c1_falta_proveedor_o_factura(
    servicio, recepciones_repo, inventario_repo, cambios, campo
):
    with pytest.raises(IdentificacionIncompletaError) as rechazo:
        servicio.registrar_recepcion(lote_de_leche(**cambios), HOY)

    assert rechazo.value.campo == campo
    afirmar_que_no_se_guardo_nada(recepciones_repo, inventario_repo)


def test_c2_datos_del_lote_invalidos(servicio, recepciones_repo, inventario_repo):
    with pytest.raises(DatosLoteInvalidosError) as rechazo:
        servicio.registrar_recepcion(lote_de_leche(cantidad=Decimal(0)), HOY)

    assert (rechazo.value.campo, rechazo.value.motivo) == (
        "cantidad",
        "debe ser mayor que cero",
    )
    afirmar_que_no_se_guardo_nada(recepciones_repo, inventario_repo)


def test_c2_lote_repetido_con_la_misma_factura(
    servicio, recepciones_repo, inventario_repo
):
    recepciones_repo.existe.return_value = True

    with pytest.raises(DatosLoteInvalidosError) as rechazo:
        servicio.registrar_recepcion(lote_de_leche(), HOY)

    assert rechazo.value.campo == "numero_lote"
    recepciones_repo.existe.assert_called_once_with("FE-2301", "L-101")
    afirmar_que_no_se_guardo_nada(recepciones_repo, inventario_repo)


@pytest.mark.parametrize(
    "cambios, motivo",
    [
        pytest.param(
            {"temperatura": Decimal("25.5")},
            "llegó a 25.5 °C y el máximo es 8 °C",
            id="temperatura 25.5",
        ),
        pytest.param(
            {"fecha_vencimiento": HOY + timedelta(days=4)},
            "le quedan 4 días y el mínimo es 5",
            id="le quedan 4 días",
        ),
    ],
)
def test_c3_lote_fuera_de_condiciones_se_guarda_rechazado_y_no_suma(
    servicio, recepciones_repo, inventario_repo, cambios, motivo
):
    registrado = servicio.registrar_recepcion(lote_de_leche(**cambios), HOY)

    assert (registrado.estado, registrado.motivo_rechazo) == (
        EstadoLote.RECHAZADO,
        motivo,
    )
    recepciones_repo.guardar.assert_called_once_with(registrado)
    recepciones_repo.confirmar.assert_called_once_with()
    inventario_repo.obtener.assert_not_called()
    inventario_repo.guardar.assert_not_called()
    inventario_repo.registrar_movimiento.assert_not_called()


def test_c4_si_falla_el_guardado_se_revierten_recepcion_y_entrada(
    servicio, ventas_repo, recepciones_repo, inventario_repo
):
    cargar_existencias(inventario_repo, leche(existencia=1000))
    recepciones_repo.guardar.side_effect = PersistenciaError(
        "base de datos no disponible"
    )
    digitado = lote_de_leche()

    with pytest.raises(PersistenciaError):
        servicio.registrar_recepcion(digitado, HOY)

    inventario_repo.guardar.assert_called_once()
    inventario_repo.revertir.assert_called_once_with()
    recepciones_repo.revertir.assert_called_once_with()
    ventas_repo.revertir.assert_called_once_with()
    recepciones_repo.confirmar.assert_not_called()
    inventario_repo.confirmar.assert_not_called()
    assert digitado.estado is EstadoLote.POR_REVISAR


def test_c5_lote_valido_se_guarda_aceptado_y_suma_existencias(
    servicio, recepciones_repo, inventario_repo
):
    lacteo = leche(existencia=1000)
    cargar_existencias(inventario_repo, lacteo)

    registrado = servicio.registrar_recepcion(lote_de_leche(), HOY)

    assert (registrado.estado, registrado.motivo_rechazo) == (EstadoLote.ACEPTADO, None)
    assert (registrado.proveedor.nombre, registrado.numero_factura) == (
        "Lácteos del Oriente",
        "FE-2301",
    )
    assert lacteo.existencia == Decimal(6000)
    inventario_repo.guardar.assert_called_once_with(lacteo)
    entrada = inventario_repo.registrar_movimiento.call_args.args[0]
    assert isinstance(entrada, EntradaInventario)
    assert (entrada.cantidad, entrada.lote) == (Decimal(5000), registrado)
    recepciones_repo.guardar.assert_called_once_with(registrado)
    recepciones_repo.confirmar.assert_called_once_with()
    inventario_repo.confirmar.assert_called_once_with()
    recepciones_repo.revertir.assert_not_called()


def test_si_falla_el_guardado_la_entrada_ya_sumada_se_descarta():
    inventario_repo = RepositorioInventario([leche(existencia=1000)])
    recepciones_repo = RepositorioRecepciones()
    unidad = UnidadDeTrabajo(RepositorioVentas(), inventario_repo, recepciones_repo)
    servicio = ServicioRecepcion(ServicioInventario(unidad), unidad)
    sin_base_de_datos = PersistenciaError("base de datos no disponible")
    falla = patch.object(recepciones_repo, "guardar", side_effect=sin_base_de_datos)

    with falla, pytest.raises(PersistenciaError):
        servicio.registrar_recepcion(lote_de_leche(), HOY)

    assert recepciones_repo.listar() == []
    assert inventario_repo.obtener("LEC").existencia == Decimal(1000)
    assert inventario_repo.movimientos() == []

    servicio.registrar_recepcion(lote_de_leche(), HOY)

    assert inventario_repo.obtener("LEC").existencia == Decimal(6000)
    assert len(inventario_repo.movimientos()) == 1
    assert recepciones_repo.existe("FE-2301", "L-101")


@pytest.mark.parametrize("sin_inventario, sin_unidad", [(True, False), (False, True)])
def test_no_se_puede_crear_el_servicio_con_dependencias_nulas(
    inventario, unidad, sin_inventario, sin_unidad
):
    with pytest.raises(ValueError, match="ServicioRecepcion necesita"):
        ServicioRecepcion(
            None if sin_inventario else inventario, None if sin_unidad else unidad
        )
