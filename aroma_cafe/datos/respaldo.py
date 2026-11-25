import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from aroma_cafe.datos.repositorios import RepositorioInventario, RepositorioRecepciones
from aroma_cafe.dominio.inventario import UnidadMedida
from aroma_cafe.dominio.recepcion import EstadoLote, LoteRecepcion, Proveedor


class Respaldo:
    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta

    def guardar(
        self, inventario: RepositorioInventario, recepciones: RepositorioRecepciones
    ) -> None:
        datos = {
            "existencias": {
                articulo.codigo: str(articulo.existencia)
                for articulo in inventario.listar()
            },
            "recepciones": [lote_a_datos(lote) for lote in recepciones.listar()],
        }
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(datos, ensure_ascii=False, indent=2)
        self.ruta.write_text(texto, encoding="utf-8")

    def restaurar(
        self, inventario: RepositorioInventario, recepciones: RepositorioRecepciones
    ) -> None:
        if not self.ruta.exists():
            return
        datos = json.loads(self.ruta.read_text(encoding="utf-8"))
        for codigo, existencia in datos["existencias"].items():
            articulo = inventario.obtener(codigo)
            articulo.existencia = Decimal(existencia)
            inventario.guardar(articulo)
        for guardado in datos["recepciones"]:
            recepciones.guardar(datos_a_lote(guardado, inventario))
        inventario.confirmar()
        recepciones.confirmar()


def lote_a_datos(lote: LoteRecepcion) -> dict[str, Any]:
    proveedor = lote.proveedor
    vencimiento = lote.fecha_vencimiento
    temperatura = lote.temperatura
    return {
        "numero_lote": lote.numero_lote,
        "articulo": lote.articulo.codigo,
        "cantidad": str(lote.cantidad),
        "unidad": lote.unidad.value,
        "responsable": lote.responsable,
        "nit": proveedor.nit if proveedor else None,
        "proveedor": proveedor.nombre if proveedor else None,
        "numero_factura": lote.numero_factura,
        "fecha_vencimiento": vencimiento.isoformat() if vencimiento else None,
        "temperatura": str(temperatura) if temperatura is not None else None,
        "estado": lote.estado.value,
        "motivo_rechazo": lote.motivo_rechazo,
    }


def datos_a_lote(
    datos: dict[str, Any], inventario: RepositorioInventario
) -> LoteRecepcion:
    nit = datos["nit"]
    vencimiento = datos["fecha_vencimiento"]
    temperatura = datos["temperatura"]
    return LoteRecepcion(
        numero_lote=datos["numero_lote"],
        articulo=inventario.obtener(datos["articulo"]),
        cantidad=Decimal(datos["cantidad"]),
        unidad=UnidadMedida(datos["unidad"]),
        responsable=datos["responsable"],
        proveedor=Proveedor(nit, datos["proveedor"]) if nit else None,
        numero_factura=datos["numero_factura"],
        fecha_vencimiento=date.fromisoformat(vencimiento) if vencimiento else None,
        temperatura=Decimal(temperatura) if temperatura is not None else None,
        estado=EstadoLote(datos["estado"]),
        motivo_rechazo=datos["motivo_rechazo"],
    )
