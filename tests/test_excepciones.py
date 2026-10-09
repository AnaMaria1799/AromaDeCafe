from decimal import Decimal

import pytest

from aroma_cafe.dominio.excepciones import (
    ArticuloNoEncontradoError,
    DatosLoteInvalidosError,
    ExistenciaInsuficienteError,
    IdentificacionIncompletaError,
    MedioPagoNoHabilitadoError,
    PagoNoConfirmadoError,
    PedidoVacioError,
    PersistenciaError,
    ReglaDeNegocioError,
)

RECHAZOS = [
    PedidoVacioError(),
    ExistenciaInsuficienteError("CAF", Decimal(0), Decimal(1)),
    MedioPagoNoHabilitadoError("tarjeta"),
    PagoNoConfirmadoError(),
    IdentificacionIncompletaError("proveedor"),
    DatosLoteInvalidosError("cantidad", "debe ser mayor que cero"),
    ArticuloNoEncontradoError("XYZ"),
]


@pytest.mark.parametrize("error", RECHAZOS, ids=lambda error: type(error).__name__)
def test_todo_rechazo_es_regla_de_negocio_con_mensaje_propio(error):
    assert isinstance(error, ReglaDeNegocioError)
    assert error.mensaje == str(error)
    assert error.mensaje


def test_ningun_rechazo_repite_el_mensaje_de_otro():
    mensajes = [error.mensaje for error in RECHAZOS]
    assert len(set(mensajes)) == len(mensajes)


def test_existencia_insuficiente_entrega_sus_datos():
    error = ExistenciaInsuficienteError("CAF", Decimal(0), Decimal(1))
    assert (error.codigo_articulo, error.existencia, error.requerida) == (
        "CAF",
        Decimal(0),
        Decimal(1),
    )
    assert error.mensaje == "Existencia insuficiente de CAF: hay 0 y se requieren 1."


def test_datos_invalidos_entrega_el_campo_y_el_motivo():
    error = DatosLoteInvalidosError("cantidad", "debe ser mayor que cero")
    assert (error.campo, error.motivo) == ("cantidad", "debe ser mayor que cero")
    assert error.mensaje == "Dato inválido en 'cantidad': debe ser mayor que cero."


def test_falla_de_persistencia_no_es_un_rechazo_de_negocio():
    assert not issubclass(PersistenciaError, ReglaDeNegocioError)
