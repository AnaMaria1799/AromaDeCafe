from datetime import date, timedelta

from tests.pantallas import abrir, texto, vender, ver


def vence_en(dias):
    return str(date.today() + timedelta(days=dias))


def recibir(cliente, **cambios):
    datos = {
        "insumo": "LEC",
        "cantidad": "5000",
        "unidad": "ml",
        "lote": "L-101",
        "vencimiento": vence_en(10),
        "temperatura": "4.0",
        "nit": "900123456-1",
        "proveedor": "Lácteos del Oriente",
        "factura": "FE-2301",
        "responsable": "Juan",
    }
    datos.update(cambios)
    return texto(cliente.post("/recepcion", data=datos))


def test_cf_007_01_lote_de_leche_valido():
    cliente = abrir()

    pagina = recibir(cliente)

    assert "Lote L-101 aceptado: entran 5000 ml de Leche." in pagina
    assert "LEC Leche 7000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_02_lote_de_cafe_sin_vencimiento_ni_temperatura():
    cliente = abrir()

    vender(cliente, latte=3)
    pagina = recibir(
        cliente,
        insumo="CAF",
        cantidad="1000",
        unidad="g",
        lote="C-55",
        vencimiento="",
        temperatura="",
        factura="FE-2302",
    )
    inventario = ver(cliente, "/inventario")

    assert "Lote C-55 aceptado: entran 1000 g de Café en grano." in pagina
    assert "CAF Café en grano 1196 g 200 Normal" in inventario
    assert "stock mínimo o por debajo" not in inventario


def test_cf_007_03_limites_que_se_aceptan():
    cliente = abrir()

    pagina = recibir(cliente, vencimiento=vence_en(5), temperatura="8.0")

    assert "Lote L-101 aceptado: entran 5000 ml de Leche." in pagina


def test_cf_007_04_sin_proveedor_o_sin_factura():
    cliente = abrir()

    sin_proveedor = recibir(cliente, nit="", proveedor="")
    sin_factura = recibir(cliente, factura="")

    assert "Recepción no registrada" in sin_proveedor
    assert 'Falta el dato obligatorio "Proveedor"' in sin_proveedor
    assert "Recepción no registrada" in sin_factura
    assert 'Falta el dato obligatorio "Número de factura"' in sin_factura
    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_05_campos_vacios_del_lote():
    cliente = abrir()

    sin_lote = recibir(cliente, lote="")
    sin_fecha = recibir(cliente, vencimiento="")
    sin_temperatura = recibir(cliente, temperatura="")

    assert 'Dato inválido en "Número de lote": es obligatorio.' in sin_lote
    assert 'Dato inválido en "Fecha de vencimiento": es obligatoria.' in sin_fecha
    assert 'Dato inválido en "Temperatura": es obligatoria.' in sin_temperatura
    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_06_cantidad_cero_o_negativa():
    cliente = abrir()

    cero = recibir(cliente, cantidad="0")
    negativa = recibir(cliente, cantidad="-1")

    assert 'Dato inválido en "Cantidad": debe ser mayor que cero.' in cero
    assert 'Dato inválido en "Cantidad": debe ser mayor que cero.' in negativa
    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_07_el_mismo_lote_dos_veces():
    cliente = abrir()

    recibir(cliente)
    pagina = recibir(cliente)

    assert 'Dato inválido en "Número de lote": ya se registró' in pagina
    assert "LEC Leche 7000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_08_limites_que_se_rechazan():
    cliente = abrir()

    caliente = recibir(cliente, temperatura="8.1")
    por_vencer = recibir(cliente, lote="L-102", vencimiento=vence_en(4))

    assert "Lote L-101 rechazado: llegó a 8.1 °C y el máximo es 8 °C." in caliente
    assert "Lote L-102 rechazado: le quedan 4 días y el mínimo es 5." in por_vencer
    assert "L-101 Leche 5000 ml" in por_vencer
    assert "L-102 Leche 5000 ml" in por_vencer
    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")


def test_cf_007_09_lotes_pendientes_de_devolucion():
    cliente = abrir()

    antes = ver(cliente, "/recepcion")
    recibir(cliente)
    pagina = recibir(cliente, lote="L-102", temperatura="25.5")

    assert "No hay lotes pendientes de devolución." in antes
    assert "L-102 Leche 5000 ml Lácteos del Oriente FE-2301" in pagina
    assert "FE-2301 llegó a 25.5 °C y el máximo es 8 °C" in pagina
    assert "L-101" not in pagina


def test_cf_007_10_unidad_que_no_corresponde_al_insumo():
    cliente = abrir()

    pagina = recibir(cliente, unidad="g")

    assert 'Dato inválido en "Unidad": este insumo se controla en ml.' in pagina
    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")
