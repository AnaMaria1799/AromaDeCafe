import json
from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.dominio.inventario import UnidadMedida
from aroma_cafe.dominio.recepcion import EstadoLote, LoteRecepcion, Proveedor
from aroma_cafe.dominio.ventas import ItemPedido, MedioPago, Producto, Venta


class Respaldo:
    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta

    def guardar(
        self,
        inventario: RepositorioInventario,
        recepciones: RepositorioRecepciones,
        ventas: RepositorioVentas,
    ) -> None:
        datos = {
            "existencias": {
                articulo.codigo: str(articulo.existencia)
                for articulo in inventario.listar()
            },
            "recepciones": [lote_a_datos(lote) for lote in recepciones.listar()],
            "ventas": [venta_a_datos(venta) for venta in ventas.listar()],
        }
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(datos, ensure_ascii=False, indent=2)
        self.ruta.write_text(texto, encoding="utf-8")

    def restaurar(
        self,
        inventario: RepositorioInventario,
        recepciones: RepositorioRecepciones,
        ventas: RepositorioVentas,
        productos: Iterable[Producto],
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
        catalogo = {producto.codigo: producto for producto in productos}
        for guardada in datos["ventas"]:
            ventas.guardar(datos_a_venta(guardada, catalogo))
        inventario.confirmar()
        recepciones.confirmar()
        ventas.confirmar()


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


def venta_a_datos(venta: Venta) -> dict[str, Any]:
    return {
        "fecha_hora": venta.fecha_hora.isoformat(),
        "empleado": venta.empleado,
        "items": [
            {"producto": item.producto.codigo, "cantidad": item.cantidad}
            for item in venta.items
        ],
        "valor_total": str(venta.valor_total),
        "medio_pago": venta.medio_pago.value,
    }


def datos_a_venta(datos: dict[str, Any], catalogo: dict[str, Producto]) -> Venta:
    items = tuple(
        ItemPedido(catalogo[item["producto"]], item["cantidad"])
        for item in datos["items"]
    )
    return Venta(
        fecha_hora=datetime.fromisoformat(datos["fecha_hora"]),
        empleado=datos["empleado"],
        items=items,
        valor_total=Decimal(datos["valor_total"]),
        medio_pago=MedioPago(datos["medio_pago"]),
    )
