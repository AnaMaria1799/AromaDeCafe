from decimal import Decimal


class ReglaDeNegocioError(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PedidoVacioError(ReglaDeNegocioError):
    def __init__(self) -> None:
        super().__init__("El pedido no tiene productos.")


class ExistenciaInsuficienteError(ReglaDeNegocioError):
    def __init__(
        self, codigo_articulo: str, existencia: Decimal, requerida: Decimal
    ) -> None:
        super().__init__(
            f"Existencia insuficiente de {codigo_articulo}: "
            f"hay {existencia} y se requieren {requerida}."
        )
        self.codigo_articulo = codigo_articulo
        self.existencia = existencia
        self.requerida = requerida


class MedioPagoNoHabilitadoError(ReglaDeNegocioError):
    def __init__(self, medio: str) -> None:
        super().__init__(f"Medio de pago no habilitado: {medio}.")
        self.medio = medio


class PagoNoConfirmadoError(ReglaDeNegocioError):
    def __init__(self) -> None:
        super().__init__("El pago no está confirmado: la venta se cancela.")


class IdentificacionIncompletaError(ReglaDeNegocioError):
    def __init__(self, campo: str) -> None:
        super().__init__(f"Falta el dato obligatorio '{campo}' de la recepción.")
        self.campo = campo


class DatosLoteInvalidosError(ReglaDeNegocioError):
    def __init__(self, campo: str, motivo: str) -> None:
        super().__init__(f"Dato inválido en '{campo}': {motivo}.")
        self.campo = campo
        self.motivo = motivo


class ArticuloNoEncontradoError(ReglaDeNegocioError):
    def __init__(self, codigo_articulo: str) -> None:
        super().__init__(f"No existe el artículo {codigo_articulo} en el inventario.")
        self.codigo_articulo = codigo_articulo


class PersistenciaError(Exception):
    pass
