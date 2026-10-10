from datetime import date

from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.excepciones import DatosLoteInvalidosError
from aroma_cafe.dominio.recepcion import LoteRecepcion
from aroma_cafe.servicios.inventario import ServicioInventario


class ServicioRecepcion:
    def __init__(self, inventario: ServicioInventario, unidad: UnidadDeTrabajo) -> None:
        if inventario is None or unidad is None:
            raise ValueError("ServicioRecepcion necesita el inventario y la unidad.")
        self._inventario = inventario
        self._unidad = unidad

    def registrar_recepcion(self, lote: LoteRecepcion, hoy: date) -> LoteRecepcion:
        lote.validar_identificacion()
        lote.validar_datos()
        if self._unidad.recepciones.existe(lote.numero_factura, lote.numero_lote):
            raise DatosLoteInvalidosError(
                "numero_lote", "ya se registró con esta factura"
            )
        motivo = lote.motivo_rechazo_por_condiciones(hoy)
        with self._unidad:
            if motivo is None:
                registrado = lote.aceptado()
                self._inventario.sumar_entrada(registrado)
            else:
                registrado = lote.rechazado(motivo)
            self._unidad.recepciones.guardar(registrado)
        return registrado
