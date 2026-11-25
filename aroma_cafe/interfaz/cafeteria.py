from dataclasses import dataclass
from decimal import Decimal

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.respaldo import Respaldo
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida
from aroma_cafe.dominio.ventas import LineaReceta, Producto
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from aroma_cafe.servicios.ventas import ServicioVentas

EMPLEADOS = ("Ana", "Cristina", "Juan")
PRODUCTOS = (
    Producto(
        "LAT",
        "Latte",
        Decimal(6500),
        (LineaReceta("CAF", Decimal(18)), LineaReceta("LEC", Decimal(200))),
    ),
    Producto("ALF", "Alfajor", Decimal(4000), (LineaReceta("ALF", Decimal(1)),)),
)


@dataclass
class Cafeteria:
    inventario_repo: RepositorioInventario
    inventario: ServicioInventario
    ventas: ServicioVentas
    recepcion: ServicioRecepcion


def abrir_cafeteria(respaldo: Respaldo | None = None) -> Cafeteria:
    cafe = ArticuloInventario(
        "CAF", "Café en grano", UnidadMedida.GRAMO, Decimal(250), Decimal(200)
    )
    leche = ArticuloInventario(
        "LEC",
        "Leche",
        UnidadMedida.MILILITRO,
        Decimal(2000),
        Decimal(500),
        maneja_vencimiento=True,
        dias_minimos=5,
        temp_maxima=Decimal(8),
    )
    alfajor = ArticuloInventario(
        "ALF", "Alfajor", UnidadMedida.UNIDAD, Decimal(1), Decimal(0)
    )
    inventario_repo = RepositorioInventario([cafe, leche, alfajor])
    recepciones_repo = RepositorioRecepciones()
    if respaldo is not None:
        respaldo.restaurar(inventario_repo, recepciones_repo)
    unidad = UnidadDeTrabajo(
        RepositorioVentas(), inventario_repo, recepciones_repo, respaldo
    )
    inventario = ServicioInventario(unidad)
    ventas = ServicioVentas(inventario, unidad)
    recepcion = ServicioRecepcion(inventario, unidad)
    return Cafeteria(inventario_repo, inventario, ventas, recepcion)
