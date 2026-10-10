from types import TracebackType

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)


class UnidadDeTrabajo:
    def __init__(
        self,
        ventas: RepositorioVentas,
        inventario: RepositorioInventario,
        recepciones: RepositorioRecepciones,
    ) -> None:
        self.ventas = ventas
        self.inventario = inventario
        self.recepciones = recepciones

    def __enter__(self) -> "UnidadDeTrabajo":
        return self

    def __exit__(
        self,
        tipo_error: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        if tipo_error is None:
            self.confirmar()
        else:
            self.revertir()

    def confirmar(self) -> None:
        self.ventas.confirmar()
        self.inventario.confirmar()
        self.recepciones.confirmar()

    def revertir(self) -> None:
        self.ventas.revertir()
        self.inventario.revertir()
        self.recepciones.revertir()
