import runpy


def test_la_demostracion_recorre_ventas_y_recepciones(capsys):
    runpy.run_module("aroma_cafe", run_name="__main__")

    salida = capsys.readouterr().out
    assert "Venta registrada por $13000 en efectivo." in salida
    assert "Alerta de abastecimiento: CAF quedó en 196 (stock mínimo 200)." in salida
    assert "Alerta de abastecimiento: ALF quedó en 0 (stock mínimo 0)." in salida
    assert "Existencia insuficiente de ALF: hay 0 y se requieren 2." in salida
    assert "Lote L-101 aceptado: entran 5000 ml de Leche." in salida
    assert "Lote L-102 rechazado: llegó a 25.5 °C y el máximo es 8 °C." in salida
    assert "Leche: 6400 ml" in salida
    assert "Ventas en el historial: 2" in salida
