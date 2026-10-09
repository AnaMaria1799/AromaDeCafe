from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal

from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida
from aroma_cafe.dominio.recepcion import LoteRecepcion, Proveedor
from aroma_cafe.dominio.ventas import (
    ItemPedido,
    LineaReceta,
    MedioPago,
    Pago,
    Pedido,
    Producto,
    Venta,
)

HOY = date(2026, 10, 6)
PROVEEDOR = Proveedor("900123456-1", "Lácteos del Oriente")
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


def leche(existencia: int = 1000) -> ArticuloInventario:
    return ArticuloInventario(
        "LEC",
        "Leche",
        UnidadMedida.MILILITRO,
        Decimal(existencia),
        Decimal(500),
        maneja_vencimiento=True,
        dias_minimos=5,
        temp_maxima=Decimal(8),
    )


def pedido(*items: ItemPedido) -> Pedido:
    return Pedido(list(items))


def pago(medio: MedioPago = MedioPago.EFECTIVO, confirmado: bool = True) -> Pago:
    return Pago(medio, confirmado)


def lote_de_leche(**cambios: object) -> LoteRecepcion:
    valido = LoteRecepcion(
        "L-101",
        leche(),
        Decimal(5000),
        UnidadMedida.MILILITRO,
        "Juan",
        PROVEEDOR,
        "FE-2301",
        HOY + timedelta(days=10),
        Decimal("4.0"),
    )
    return replace(valido, **cambios)
