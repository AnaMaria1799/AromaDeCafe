from datetime import datetime
from decimal import Decimal

from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida
from aroma_cafe.dominio.ventas import (
    ItemPedido,
    LineaReceta,
    MedioPago,
    Pago,
    Pedido,
    Producto,
    Venta,
)

LATTE = Producto(
    "LAT",
    "Latte",
    Decimal(6500),
    (LineaReceta("CAF", Decimal(18)), LineaReceta("LEC", Decimal(200))),
)
TINTO = Producto("TIN", "Tinto", Decimal(3000), (LineaReceta("CAF", Decimal(10)),))
VENTA = Venta(
    datetime(2026, 10, 6, 9, 30),
    "Ana",
    (ItemPedido(LATTE, 1),),
    Decimal(6500),
    MedioPago.EFECTIVO,
)


def cafe(existencia: int = 100, stock_minimo: int = 20) -> ArticuloInventario:
    return ArticuloInventario(
        "CAF",
        "Café en grano",
        UnidadMedida.GRAMO,
        Decimal(existencia),
        Decimal(stock_minimo),
    )


def pedido(*items: ItemPedido) -> Pedido:
    return Pedido(list(items))


def pago(medio: MedioPago = MedioPago.EFECTIVO, confirmado: bool = True) -> Pago:
    return Pago(medio, confirmado)
