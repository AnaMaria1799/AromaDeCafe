from decimal import Decimal

from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import ExistenciaInsuficienteError


class ServicioInventario:
    def __init__(self, unidad: UnidadDeTrabajo) -> None:
        if unidad is None:
            raise ValueError("ServicioInventario necesita la unidad de trabajo.")
        self._unidad = unidad

    def verificar_disponibilidad(self, consumos: dict[str, Decimal]) -> None:
        for codigo, cantidad in consumos.items():
            articulo = self._unidad.inventario.obtener(codigo)
            if not articulo.hay_disponibilidad(cantidad):
                raise ExistenciaInsuficienteError(codigo, articulo.existencia, cantidad)
