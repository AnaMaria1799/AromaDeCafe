from tests.pantallas import abrir, vender, ver


def test_cf_001_01_dos_latte_en_efectivo():
    cliente = abrir()

    pagina = vender(cliente, latte=2)

    assert "Venta registrada por $13000 en efectivo." in pagina
    assert "2 Latte $13000 efectivo Ana" in pagina


def test_cf_001_02_un_latte_y_el_ultimo_alfajor_con_tarjeta():
    cliente = abrir()

    pagina = vender(cliente, latte=1, alfajor=1, medio="tarjeta")

    assert "Venta registrada por $10500 en tarjeta." in pagina
    assert "Alerta de abastecimiento: ALF quedó en 0 (stock mínimo 0)." in pagina
    assert "1 Latte, 1 Alfajor $10500 tarjeta Ana" in pagina


def test_cf_001_03_pedido_sin_productos():
    cliente = abrir()

    pagina = vender(cliente)

    assert "Venta rechazada: El pedido no tiene productos." in pagina
    assert "Todavía no hay ventas." in pagina


def test_cf_001_04_cantidad_negativa():
    cliente = abrir()

    formulario = cliente.get("/ventas").get_data(as_text=True)
    pagina = vender(cliente, latte=-1)

    assert 'name="LAT" value="0" min="0"' in formulario
    assert "Venta rechazada: La cantidad de un ítem debe ser mayor que cero." in pagina
    assert "Todavía no hay ventas." in pagina


def test_cf_001_05_piden_mas_alfajores_de_los_que_hay():
    cliente = abrir()

    pagina = vender(cliente, alfajor=2)

    assert (
        "Venta rechazada: Existencia insuficiente de ALF: hay 1 y se requieren 2."
        in pagina
    )
    assert "Todavía no hay ventas." in pagina


def test_cf_001_06_sin_confirmar_el_pago_no_se_registra():
    cliente = abrir()

    formulario = cliente.get("/ventas").get_data(as_text=True)
    pagina = vender(cliente, latte=1, medio="transferencia", confirmado=False)

    assert '<button id="registrar" type="submit" disabled>' in formulario
    assert "Venta rechazada: El pago no está confirmado: la venta se cancela." in pagina
    assert "Todavía no hay ventas." in pagina


def test_cf_001_07_solo_se_ofrecen_los_medios_habilitados():
    cliente = abrir()

    formulario = cliente.get("/ventas").get_data(as_text=True)
    pantalla = ver(cliente, "/ventas")
    pagina = vender(cliente, latte=1, medio="transferencia")

    assert 'value="efectivo" checked' in formulario
    assert "Medio de pago Efectivo Tarjeta Transferencia Confirmación" in pantalla
    assert "Venta registrada por $6500 en transferencia." in pagina


def test_cf_001_08_el_historial_muestra_cada_venta_con_su_empleado():
    cliente = abrir()

    vender(cliente, latte=2)
    pagina = vender(cliente, alfajor=1, medio="tarjeta", empleado="Cristina")

    assert "2 Latte $13000 efectivo Ana" in pagina
    assert "1 Alfajor $4000 tarjeta Cristina" in pagina
