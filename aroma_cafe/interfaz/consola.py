from datetime import date

from aroma_cafe.dominio.excepciones import PersistenciaError, ReglaDeNegocioError
from aroma_cafe.dominio.recepcion import EstadoLote, LoteRecepcion
from aroma_cafe.dominio.ventas import Pago, Pedido
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from aroma_cafe.servicios.ventas import ServicioVentas


def registrar_venta(
    servicio: ServicioVentas, pedido: Pedido, pago: Pago, empleado: str
) -> str:
    try:
        registro = servicio.registrar_venta(pedido, pago, empleado)
    except ReglaDeNegocioError as error:
        return f"Venta rechazada: {error.mensaje}"
    except PersistenciaError:
        return "No se pudo guardar la venta. Intente de nuevo."
    venta = registro.venta
    lineas = [f"Venta registrada por ${venta.valor_total} en {venta.medio_pago.value}."]
    for alerta in registro.alertas:
        lineas.append(
            f"  Alerta de abastecimiento: {alerta.codigo_articulo} quedó en "
            f"{alerta.existencia} (stock mínimo {alerta.stock_minimo})."
        )
    return "\n".join(lineas)


def registrar_recepcion(
    servicio: ServicioRecepcion, lote: LoteRecepcion, hoy: date
) -> str:
    try:
        registrado = servicio.registrar_recepcion(lote, hoy)
    except ReglaDeNegocioError as error:
        return f"Recepción no registrada: {error.mensaje}"
    except PersistenciaError:
        return "No se pudo guardar la recepción. Intente de nuevo."
    if registrado.estado is EstadoLote.RECHAZADO:
        return f"Lote {registrado.numero_lote} rechazado: {registrado.motivo_rechazo}."
    return (
        f"Lote {registrado.numero_lote} aceptado: entran {registrado.cantidad} "
        f"{registrado.unidad.value} de {registrado.articulo.nombre}."
    )
