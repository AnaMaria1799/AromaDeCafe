from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class UnidadMedida(Enum):
    GRAMO = "g"
    MILILITRO = "ml"
    UNIDAD = "und"


@dataclass
class ArticuloInventario:
    codigo: str
    nombre: str
    unidad: UnidadMedida
    existencia: Decimal
    stock_minimo: Decimal
    maneja_vencimiento: bool = False
    dias_minimos: int = 0
    temp_maxima: Decimal | None = None

    def hay_disponibilidad(self, cantidad: Decimal) -> bool:
        return self.existencia >= cantidad

    def descontar(self, cantidad: Decimal) -> None:
        self.existencia -= cantidad

    def sumar(self, cantidad: Decimal) -> None:
        self.existencia += cantidad

    def requiere_reposicion(self) -> bool:
        return self.existencia <= self.stock_minimo


@dataclass(frozen=True)
class AlertaAbastecimiento:
    codigo_articulo: str
    existencia: Decimal
    stock_minimo: Decimal
    fecha_hora: datetime
