from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum

from aroma_cafe.dominio.inventario import AlertaAbastecimiento


class MedioPago(Enum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"


@dataclass(frozen=True)
class LineaReceta:
    codigo_articulo: str
    cantidad_por_unidad: Decimal

    def __post_init__(self) -> None:
        if self.cantidad_por_unidad <= 0:
            raise ValueError("La cantidad de una receta debe ser mayor que cero.")


@dataclass(frozen=True)
class Producto:
    codigo: str
    nombre: str
    precio: Decimal
    receta: tuple[LineaReceta, ...]

    def __post_init__(self) -> None:
        if not self.receta:
            raise ValueError("Un producto necesita al menos una línea de receta.")


@dataclass(frozen=True)
class ItemPedido:
    producto: Producto
    cantidad: int

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise ValueError("La cantidad de un ítem debe ser mayor que cero.")

    def subtotal(self) -> Decimal:
        return self.producto.precio * self.cantidad


@dataclass
class Pedido:
    items: list[ItemPedido] = field(default_factory=list)

    def esta_vacio(self) -> bool:
        return not self.items

    def consumos(self) -> dict[str, Decimal]:
        totales: dict[str, Decimal] = {}
        for item in self.items:
            for linea in item.producto.receta:
                cantidad = linea.cantidad_por_unidad * item.cantidad
                acumulado = totales.get(linea.codigo_articulo, Decimal(0))
                totales[linea.codigo_articulo] = acumulado + cantidad
        return totales

    def valor_total(self) -> Decimal:
        return sum((item.subtotal() for item in self.items), Decimal(0))


@dataclass(frozen=True)
class Pago:
    medio: MedioPago
    confirmado: bool

    def __post_init__(self) -> None:
        if not isinstance(self.medio, MedioPago):
            raise ValueError("El pago debe indicar un medio de pago.")


@dataclass(frozen=True)
class Venta:
    fecha_hora: datetime
    empleado: str
    items: tuple[ItemPedido, ...]
    valor_total: Decimal
    medio_pago: MedioPago


@dataclass(frozen=True)
class VentaRegistrada:
    venta: Venta
    alertas: tuple[AlertaAbastecimiento, ...]
