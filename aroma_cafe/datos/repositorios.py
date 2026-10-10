from collections.abc import Iterable
from dataclasses import replace
from typing import Generic, TypeVar

from aroma_cafe.dominio.excepciones import ArticuloNoEncontradoError
from aroma_cafe.dominio.inventario import ArticuloInventario
from aroma_cafe.dominio.movimientos import MovimientoInventario
from aroma_cafe.dominio.recepcion import LoteRecepcion
from aroma_cafe.dominio.ventas import Venta

T = TypeVar("T")


class RepositorioDeRegistros(Generic[T]):
    def __init__(self) -> None:
        self._guardados: list[T] = []
        self._pendientes: list[T] = []

    def guardar(self, registro: T) -> None:
        self._pendientes.append(registro)

    def listar(self) -> list[T]:
        return list(self._guardados)

    def confirmar(self) -> None:
        self._guardados.extend(self._pendientes)
        self._pendientes.clear()

    def revertir(self) -> None:
        self._pendientes.clear()


class RepositorioVentas(RepositorioDeRegistros[Venta]):
    pass


class RepositorioRecepciones(RepositorioDeRegistros[LoteRecepcion]):
    def existe(self, numero_factura: str | None, numero_lote: str) -> bool:
        return any(
            lote.numero_factura == numero_factura and lote.numero_lote == numero_lote
            for lote in self._guardados
        )


class RepositorioInventario:
    def __init__(self, articulos: Iterable[ArticuloInventario] = ()) -> None:
        self._guardados = {articulo.codigo: articulo for articulo in articulos}
        self._pendientes: dict[str, ArticuloInventario] = {}
        self._movimientos = RepositorioDeRegistros[MovimientoInventario]()

    def obtener(self, codigo: str) -> ArticuloInventario:
        if codigo not in self._guardados:
            raise ArticuloNoEncontradoError(codigo)
        return replace(self._guardados[codigo])

    def guardar(self, articulo: ArticuloInventario) -> None:
        self._pendientes[articulo.codigo] = articulo

    def registrar_movimiento(self, movimiento: MovimientoInventario) -> None:
        self._movimientos.guardar(movimiento)

    def movimientos(self) -> list[MovimientoInventario]:
        return self._movimientos.listar()

    def confirmar(self) -> None:
        self._guardados.update(self._pendientes)
        self._pendientes.clear()
        self._movimientos.confirmar()

    def revertir(self) -> None:
        self._pendientes.clear()
        self._movimientos.revertir()
