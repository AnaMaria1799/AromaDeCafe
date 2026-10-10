from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from aroma_cafe.dominio.recepcion import LoteRecepcion
from aroma_cafe.dominio.ventas import Venta


@dataclass(frozen=True)
class MovimientoInventario:
    fecha_hora: datetime
    codigo_articulo: str
    cantidad: Decimal
    responsable: str


@dataclass(frozen=True)
class SalidaInventario(MovimientoInventario):
    venta: Venta


@dataclass(frozen=True)
class EntradaInventario(MovimientoInventario):
    lote: LoteRecepcion
