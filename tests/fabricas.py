from decimal import Decimal

from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida


def cafe(existencia: int = 100, stock_minimo: int = 20) -> ArticuloInventario:
    return ArticuloInventario(
        "CAF",
        "Café en grano",
        UnidadMedida.GRAMO,
        Decimal(existencia),
        Decimal(stock_minimo),
    )
