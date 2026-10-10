from decimal import Decimal

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.dominio.excepciones import ArticuloNoEncontradoError
from aroma_cafe.dominio.movimientos import SalidaInventario
from tests.fabricas import VENTA, cafe, lote_de_leche


def test_una_venta_guardada_no_aparece_hasta_confirmar():
    ventas = RepositorioVentas()
    ventas.guardar(VENTA)
    assert ventas.listar() == []
    ventas.confirmar()
    assert ventas.listar() == [VENTA]


def test_revertir_descarta_lo_pendiente():
    ventas = RepositorioVentas()
    ventas.guardar(VENTA)
    ventas.revertir()
    ventas.confirmar()
    assert ventas.listar() == []


def test_obtener_entrega_una_copia_y_no_el_articulo_guardado():
    inventario = RepositorioInventario([cafe(existencia=100)])
    copia = inventario.obtener("CAF")
    copia.descontar(Decimal(18))
    assert inventario.obtener("CAF").existencia == Decimal(100)


def test_obtener_un_codigo_que_no_existe_lanza_error():
    inventario = RepositorioInventario([cafe()])
    with pytest.raises(ArticuloNoEncontradoError) as rechazo:
        inventario.obtener("XYZ")
    assert rechazo.value.codigo_articulo == "XYZ"


def test_la_existencia_y_el_movimiento_cambian_solo_al_confirmar():
    inventario = RepositorioInventario([cafe(existencia=100)])
    salida = SalidaInventario(VENTA.fecha_hora, "CAF", Decimal(18), "Ana", VENTA)
    inventario.guardar(cafe(existencia=82))
    inventario.registrar_movimiento(salida)
    assert inventario.obtener("CAF").existencia == Decimal(100)
    assert inventario.movimientos() == []
    inventario.confirmar()
    assert inventario.obtener("CAF").existencia == Decimal(82)
    assert inventario.movimientos() == [salida]


def test_revertir_deja_la_existencia_y_los_movimientos_como_estaban():
    inventario = RepositorioInventario([cafe(existencia=100)])
    salida = SalidaInventario(VENTA.fecha_hora, "CAF", Decimal(18), "Ana", VENTA)
    inventario.guardar(cafe(existencia=82))
    inventario.registrar_movimiento(salida)
    inventario.revertir()
    inventario.confirmar()
    assert inventario.obtener("CAF").existencia == Decimal(100)
    assert inventario.movimientos() == []


def test_existe_distingue_la_factura_y_el_numero_de_lote():
    recepciones = RepositorioRecepciones()
    recepciones.guardar(lote_de_leche())
    recepciones.confirmar()
    assert recepciones.existe("FE-2301", "L-101")
    assert not recepciones.existe("FE-2301", "L-102")
    assert not recepciones.existe("FE-9999", "L-101")
