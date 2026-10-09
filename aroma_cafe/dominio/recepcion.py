from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from enum import Enum

from aroma_cafe.dominio.excepciones import (
    DatosLoteInvalidosError,
    IdentificacionIncompletaError,
)
from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida


class EstadoLote(Enum):
    POR_REVISAR = "por revisar"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado, pendiente de devolución"


@dataclass(frozen=True)
class Proveedor:
    nit: str
    nombre: str


@dataclass(frozen=True)
class LoteRecepcion:
    numero_lote: str
    articulo: ArticuloInventario
    cantidad: Decimal
    unidad: UnidadMedida
    responsable: str
    proveedor: Proveedor | None = None
    numero_factura: str | None = None
    fecha_vencimiento: date | None = None
    temperatura: Decimal | None = None
    estado: EstadoLote = EstadoLote.POR_REVISAR
    motivo_rechazo: str | None = None

    def validar_identificacion(self) -> None:
        if self.proveedor is None:
            raise IdentificacionIncompletaError("proveedor")
        if not self.numero_factura:
            raise IdentificacionIncompletaError("numero_factura")

    def validar_datos(self) -> None:
        articulo = self.articulo
        if not self.numero_lote:
            raise DatosLoteInvalidosError("numero_lote", "es obligatorio")
        if self.cantidad <= 0:
            raise DatosLoteInvalidosError("cantidad", "debe ser mayor que cero")
        if self.unidad != articulo.unidad:
            motivo = f"este insumo se controla en {articulo.unidad.value}"
            raise DatosLoteInvalidosError("unidad", motivo)
        if articulo.maneja_vencimiento and self.fecha_vencimiento is None:
            raise DatosLoteInvalidosError("fecha_vencimiento", "es obligatoria")
        if articulo.temp_maxima is not None and self.temperatura is None:
            raise DatosLoteInvalidosError("temperatura", "es obligatoria")

    def motivo_rechazo_por_condiciones(self, hoy: date) -> str | None:
        articulo = self.articulo
        if self.fecha_vencimiento is not None:
            dias = (self.fecha_vencimiento - hoy).days
            if dias < articulo.dias_minimos:
                return f"le quedan {dias} días y el mínimo es {articulo.dias_minimos}"
        if (
            self.temperatura is not None
            and articulo.temp_maxima is not None
            and self.temperatura > articulo.temp_maxima
        ):
            maxima = articulo.temp_maxima
            return f"llegó a {self.temperatura} °C y el máximo es {maxima} °C"
        return None

    def aceptado(self) -> "LoteRecepcion":
        return replace(self, estado=EstadoLote.ACEPTADO)

    def rechazado(self, motivo: str) -> "LoteRecepcion":
        return replace(self, estado=EstadoLote.RECHAZADO, motivo_rechazo=motivo)
