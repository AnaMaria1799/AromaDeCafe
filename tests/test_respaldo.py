from datetime import date, timedelta

from aroma_cafe.datos.respaldo import Respaldo
from aroma_cafe.interfaz.web import crear_app
from tests.pantallas import texto, vender, ver


def abrir_con_respaldo(ruta):
    return crear_app(Respaldo(ruta)).test_client()


def recibir(cliente, **cambios):
    datos = {
        "insumo": "LEC",
        "cantidad": "5000",
        "unidad": "ml",
        "lote": "L-101",
        "vencimiento": str(date.today() + timedelta(days=10)),
        "temperatura": "4.0",
        "nit": "900123456-1",
        "proveedor": "Lácteos del Oriente",
        "factura": "FE-2301",
        "responsable": "Juan",
    }
    datos.update(cambios)
    return texto(cliente.post("/recepcion", data=datos))


def test_sin_respaldo_arranca_con_los_datos_iniciales(tmp_path):
    cliente = abrir_con_respaldo(tmp_path / "aroma_cafe.json")

    assert "LEC Leche 2000 ml 500 Normal" in ver(cliente, "/inventario")
    assert not (tmp_path / "aroma_cafe.json").exists()


def test_el_lote_aceptado_se_recupera_al_abrir_de_nuevo(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"
    recibir(abrir_con_respaldo(ruta))

    cliente = abrir_con_respaldo(ruta)
    repetido = recibir(cliente)

    assert "LEC Leche 7000 ml 500 Normal" in ver(cliente, "/inventario")
    assert 'Dato inválido en "Número de lote": ya se registró' in repetido


def test_el_lote_rechazado_sigue_pendiente_de_devolucion(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"
    recibir(abrir_con_respaldo(ruta), lote="L-102", temperatura="25.5")

    pagina = ver(abrir_con_respaldo(ruta), "/recepcion")

    assert "L-102 Leche 5000 ml Lácteos del Oriente FE-2301" in pagina
    assert "llegó a 25.5 °C y el máximo es 8 °C" in pagina


def test_el_lote_sin_vencimiento_ni_temperatura_se_recupera(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"
    recibir(
        abrir_con_respaldo(ruta),
        insumo="CAF",
        cantidad="1000",
        unidad="g",
        lote="C-55",
        vencimiento="",
        temperatura="",
    )

    cliente = abrir_con_respaldo(ruta)

    assert "CAF Café en grano 1250 g 200 Normal" in ver(cliente, "/inventario")


def test_una_recepcion_no_registrada_no_crea_respaldo(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"

    recibir(abrir_con_respaldo(ruta), factura="")

    assert not ruta.exists()


def test_la_venta_y_su_descuento_se_recuperan_al_abrir_de_nuevo(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"
    vender(abrir_con_respaldo(ruta), latte=2, empleado="Cristina")

    cliente = abrir_con_respaldo(ruta)

    assert "2 Latte $13000 efectivo Cristina" in ver(cliente, "/ventas")
    assert "CAF Café en grano 214 g 200 Normal" in ver(cliente, "/inventario")
    assert "LEC Leche 1600 ml 500 Normal" in ver(cliente, "/inventario")


def test_una_venta_rechazada_no_queda_en_el_respaldo(tmp_path):
    ruta = tmp_path / "aroma_cafe.json"
    cliente = abrir_con_respaldo(ruta)
    vender(cliente, latte=1)

    vender(cliente, alfajor=2)

    nuevo = abrir_con_respaldo(ruta)
    assert "1 Latte $6500 efectivo Ana" in ver(nuevo, "/ventas")
    assert "ALF Alfajor 1 und 0 Normal" in ver(nuevo, "/inventario")
