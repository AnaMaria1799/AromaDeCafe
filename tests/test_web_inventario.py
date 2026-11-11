from tests.pantallas import abrir, vender, ver


def test_cf_005_01_la_venta_descuenta_segun_la_receta():
    cliente = abrir()

    antes = ver(cliente, "/inventario")
    vender(cliente, latte=2)
    despues = ver(cliente, "/inventario")

    assert "CAF Café en grano 250 g 200 Normal" in antes
    assert "CAF Café en grano 214 g 200 Normal" in despues
    assert "LEC Leche 1600 ml 500 Normal" in despues
    assert "ALF Alfajor 1 und 0 Normal" in despues


def test_cf_005_02_el_cafe_queda_por_debajo_del_minimo():
    cliente = abrir()

    venta = vender(cliente, latte=3)
    inventario = ver(cliente, "/inventario")

    assert "Alerta de abastecimiento: CAF quedó en 196 (stock mínimo 200)." in venta
    assert "CAF Café en grano 196 g 200 Reponer" in inventario
    assert "stock mínimo o por debajo: Café en grano." in inventario


def test_cf_005_03_el_alfajor_queda_justo_en_el_minimo():
    cliente = abrir()

    venta = vender(cliente, alfajor=1)
    inventario = ver(cliente, "/inventario")

    assert "Alerta de abastecimiento: ALF quedó en 0 (stock mínimo 0)." in venta
    assert "ALF Alfajor 0 und 0 Reponer" in inventario
    assert "stock mínimo o por debajo: Alfajor." in inventario


def test_cf_005_04_las_ventas_rechazadas_no_cambian_el_inventario():
    cliente = abrir()

    vender(cliente, alfajor=2)
    vender(cliente)
    inventario = ver(cliente, "/inventario")

    assert "CAF Café en grano 250 g 200 Normal" in inventario
    assert "LEC Leche 2000 ml 500 Normal" in inventario
    assert "ALF Alfajor 1 und 0 Normal" in inventario


def test_cf_005_05_dos_cajas_venden_el_ultimo_alfajor():
    cliente = abrir()

    primera = vender(cliente, alfajor=1, empleado="Ana")
    segunda = vender(cliente, alfajor=1, empleado="Cristina")
    inventario = ver(cliente, "/inventario")

    assert "Venta registrada por $4000 en efectivo." in primera
    assert "Existencia insuficiente de ALF: hay 0 y se requieren 1." in segunda
    assert "ALF Alfajor 0 und 0 Reponer" in inventario


def test_cf_005_06_la_leche_alcanza_para_10_latte_y_no_para_11():
    con_diez = abrir()
    con_once = abrir()

    diez = vender(con_diez, latte=10)
    once = vender(con_once, latte=11)
    inventario = ver(con_once, "/inventario")

    assert "Venta registrada por $65000 en efectivo." in diez
    assert "Alerta de abastecimiento: LEC quedó en 0 (stock mínimo 500)." in diez
    assert "Existencia insuficiente de LEC: hay 2000 y se requieren 2200." in once
    assert "CAF Café en grano 250 g 200 Normal" in inventario
    assert "LEC Leche 2000 ml 500 Normal" in inventario


def test_cf_005_07_insumos_por_reponer():
    cliente = abrir()

    antes = ver(cliente, "/inventario")
    vender(cliente, latte=3)
    vender(cliente, alfajor=1)
    despues = ver(cliente, "/inventario")

    assert "stock mínimo o por debajo" not in antes
    assert "stock mínimo o por debajo: Café en grano, Alfajor." in despues
    assert "LEC Leche 1400 ml 500 Normal" in despues


def test_cf_005_08_la_existencia_no_se_puede_cambiar_a_mano():
    cliente = abrir()

    pagina = cliente.get("/inventario").get_data(as_text=True)

    assert "<form" not in pagina
    assert "<input" not in pagina
    assert "<button" not in pagina
