from datetime import date, timedelta
from threading import Thread
from time import perf_counter

from aroma_cafe.interfaz.web import crear_app
from tests.pantallas import ver

VENTAS_POR_USUARIO = 20
LOTES_POR_USUARIO = 5


def recibir(cliente, insumo, cantidad, unidad, lote, **extra):
    datos = {
        "insumo": insumo,
        "cantidad": cantidad,
        "unidad": unidad,
        "lote": lote,
        "nit": "900123456-1",
        "proveedor": "Lácteos del Oriente",
        "factura": "FE-9000",
        "responsable": "Juan",
    }
    datos.update(extra)
    cliente.post("/recepcion", data=datos)


def preparar_existencias(cliente):
    recibir(cliente, "CAF", "2000", "g", "C-0")
    recibir(
        cliente,
        "LEC",
        "20000",
        "ml",
        "L-0",
        vencimiento=str(date.today() + timedelta(days=10)),
        temperatura="4.0",
    )


def trabajar(app, empleado, tiempos):
    cliente = app.test_client()
    venta = {"empleado": empleado, "LAT": "1", "medio": "efectivo", "confirmado": "si"}
    for _ in range(VENTAS_POR_USUARIO):
        inicio = perf_counter()
        cliente.post("/ventas", data=venta)
        tiempos.append(perf_counter() - inicio)
    for numero in range(LOTES_POR_USUARIO):
        inicio = perf_counter()
        recibir(cliente, "CAF", "100", "g", f"{empleado}-{numero}")
        tiempos.append(perf_counter() - inicio)


def percentil_95(tiempos):
    ordenados = sorted(tiempos)
    return ordenados[int(len(ordenados) * 0.95) - 1]


def test_rnf_2_tres_usuarios_a_la_vez_en_menos_de_3_segundos():
    app = crear_app()
    preparar_existencias(app.test_client())
    tiempos = []
    usuarios = [
        Thread(target=trabajar, args=(app, empleado, tiempos))
        for empleado in ("Ana", "Cristina", "Juan")
    ]

    for usuario in usuarios:
        usuario.start()
    for usuario in usuarios:
        usuario.join()

    inventario = ver(app.test_client(), "/inventario")
    assert len(tiempos) == 75
    assert percentil_95(tiempos) <= 3
    assert "CAF Café en grano 2670 g 200 Normal" in inventario
    assert "LEC Leche 10000 ml 500 Normal" in inventario
