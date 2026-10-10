from decimal import Decimal

from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import ExistenciaInsuficienteError
from aroma_cafe.dominio.inventario import AlertaAbastecimiento
from aroma_cafe.dominio.movimientos import SalidaInventario
from aroma_cafe.dominio.ventas import Venta


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

    def descontar_por_venta(
        self, venta: Venta, consumos: dict[str, Decimal]
    ) -> list[AlertaAbastecimiento]:
        alertas = []
        for codigo, cantidad in consumos.items():
            articulo = self._unidad.inventario.obtener(codigo)
            if not articulo.hay_disponibilidad(cantidad):
                raise ExistenciaInsuficienteError(codigo, articulo.existencia, cantidad)
            articulo.descontar(cantidad)
            self._unidad.inventario.guardar(articulo)
            self._unidad.inventario.registrar_movimiento(
                SalidaInventario(
                    venta.fecha_hora, codigo, cantidad, venta.empleado, venta
                )
            )
            if articulo.requiere_reposicion():
                alertas.append(
                    AlertaAbastecimiento(
                        codigo,
                        articulo.existencia,
                        articulo.stock_minimo,
                        venta.fecha_hora,
                    )
                )
        return alertas
