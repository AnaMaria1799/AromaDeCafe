from datetime import datetime

from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import (
    MedioPagoNoHabilitadoError,
    PagoNoConfirmadoError,
    PedidoVacioError,
)
from aroma_cafe.dominio.ventas import MedioPago, Pago, Pedido, Venta, VentaRegistrada
from aroma_cafe.servicios.inventario import ServicioInventario


class ServicioVentas:
    def __init__(
        self,
        inventario: ServicioInventario,
        unidad: UnidadDeTrabajo,
        medios_habilitados: frozenset[MedioPago] = frozenset(MedioPago),
    ) -> None:
        if inventario is None or unidad is None:
            raise ValueError("ServicioVentas necesita el inventario y la unidad.")
        self._inventario = inventario
        self._unidad = unidad
        self._medios_habilitados = medios_habilitados

    def registrar_venta(
        self, pedido: Pedido, pago: Pago, empleado: str
    ) -> VentaRegistrada:
        if pedido.esta_vacio():
            raise PedidoVacioError()
        consumos = pedido.consumos()
        self._inventario.verificar_disponibilidad(consumos)
        if pago.medio not in self._medios_habilitados:
            raise MedioPagoNoHabilitadoError(pago.medio.value)
        if not pago.confirmado:
            raise PagoNoConfirmadoError()
        venta = Venta(
            datetime.now(),
            empleado,
            tuple(pedido.items),
            pedido.valor_total(),
            pago.medio,
        )
        with self._unidad:
            self._unidad.ventas.guardar(venta)
            alertas = self._inventario.descontar_por_venta(venta, consumos)
        return VentaRegistrada(venta, tuple(alertas))
