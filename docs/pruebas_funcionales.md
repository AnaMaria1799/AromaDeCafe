# Reporte de pruebas funcionales · Sprint 6

Pantallas web de Aroma de Café: Ventas (HU-001), Inventario (HU-005) y Recepción
(HU-007). Los casos son los del RTF4 corregido, de CF-001-01 a CF-007-10.

## Cómo se ejecutaron

- **Automáticas:** cada caso tiene una prueba con su ID en el nombre. La prueba abre
  la aplicación desde cero, envía el formulario como lo hace el navegador y revisa
  solo el texto que se ve en la página. Se corren con:

      python -m pytest tests/test_web_ventas.py tests/test_web_inventario.py tests/test_web_recepcion.py -v --no-cov

  La salida completa está en `docs/resultado_pruebas_funcionales.txt`. GitHub Actions
  las repite en cada push y pull request, junto con las demás pruebas.
- **Manuales:** cada responsable abrió la aplicación con
  `python -m flask --app aroma_cafe.interfaz.web run`, siguió en el navegador los
  pasos del RTF4 de dos casos de su pantalla y dejó la captura en su tarea de pruebas
  de Jira.

## Resultado

| HU | Pantalla | Casos | Archivo de pruebas | Revisados a mano | Resultado |
|---|---|---|---|---|---|
| HU-001 | Ventas | CF-001-01 a CF-001-08 | `tests/test_web_ventas.py` | CF-001-01 y CF-001-06 (Ana) | 8 de 8 pasan |
| HU-005 | Inventario | CF-005-01 a CF-005-08 | `tests/test_web_inventario.py` | CF-005-05 y CF-005-07 (Cristina) | 8 de 8 pasan |
| HU-007 | Recepción | CF-007-01 a CF-007-10 | `tests/test_web_recepcion.py` | CF-007-04 y CF-007-09 (Juan) | 10 de 10 pasan |

En total pasan 26 de 26 casos. Con las pruebas unitarias del RTF3, el
proyecto tiene 149 pruebas, con 100 % de cobertura.

## Detalle por caso

| ID | Qué se hace | Lo que debe verse | Prueba | Resultado |
|---|---|---|---|---|
| CF-001-01 | Ventas: en Cantidad de Latte escribir 2, dejar Efectivo, marcar «El pago ha sido confirmado» y pulsar Registrar Venta. | Mensaje verde «Venta registrada por $13000 en efectivo.» y, en Ventas de hoy, la fila 2 Latte · $13000 · efectivo · Ana. | `test_cf_001_01_dos_latte_en_efectivo` | Pasa |
| CF-001-02 | Ventas: Latte = 1 y Alfajor = 1 (queda 1), marcar Tarjeta y la casilla, pulsar Registrar Venta. | «Venta registrada por $10500 en tarjeta.» y, en amarillo, «Alerta de abastecimiento: ALF quedó en 0 (stock mínimo 0).» | `test_cf_001_02_un_latte_y_el_ultimo_alfajor_con_tarjeta` | Pasa |
| CF-001-03 | Ventas: dejar las cantidades en 0, marcar la casilla y pulsar Registrar Venta. | Mensaje rojo «Venta rechazada: El pedido no tiene productos.» y Ventas de hoy dice «Todavía no hay ventas.» | `test_cf_001_03_pedido_sin_productos` | Pasa |
| CF-001-04 | Ventas: escribir -1 en Cantidad de Latte, marcar la casilla y pulsar Registrar Venta. | El navegador no envía el formulario y señala Cantidad (el mínimo es 0). Si el dato llega por fuera del navegador: «Venta rechazada: La cantidad de un ítem debe ser mayor que cero.» | `test_cf_001_04_cantidad_negativa` | Pasa |
| CF-001-05 | Ventas: escribir 2 en Cantidad de Alfajor (queda 1), marcar la casilla y pulsar Registrar Venta. | Mensaje rojo «Venta rechazada: Existencia insuficiente de ALF: hay 1 y se requieren 2.» y Ventas de hoy sigue vacía. | `test_cf_001_05_piden_mas_alfajores_de_los_que_hay` | Pasa |
| CF-001-06 | Ventas: Latte = 1 y Transferencia, sin marcar «El pago ha sido confirmado»; intentar pulsar Registrar Venta. | El botón está gris y no responde; se activa solo al marcar la casilla. Si el formulario llega sin la casilla: «Venta rechazada: El pago no está confirmado: la venta se cancela.» | `test_cf_001_06_sin_confirmar_el_pago_no_se_registra` | Pasa |
| CF-001-07 | Ventas: revisar las opciones de Medio de pago; registrar 1 Latte con Transferencia. | Solo aparecen Efectivo (marcado al abrir), Tarjeta y Transferencia, y siempre hay uno marcado. Sale «Venta registrada por $6500 en transferencia.» | `test_cf_001_07_solo_se_ofrecen_los_medios_habilitados` | Pasa |
| CF-001-08 | Ventas: registrar 2 Latte (Ana, Efectivo) y después 1 Alfajor (Empleado Cristina, Tarjeta). | Ventas de hoy muestra las dos filas en orden, cada una con su hora: 2 Latte · $13000 · efectivo · Ana y 1 Alfajor · $4000 · tarjeta · Cristina. | `test_cf_001_08_el_historial_muestra_cada_venta_con_su_empleado` | Pasa |
| CF-005-01 | Abrir Inventario; en Ventas registrar 2 Latte; volver a Inventario. | Primero 250 g, 2000 ml y 1 und, todos en Normal. Después, la fila Café en grano muestra 214 g y la de Leche 1600 ml, en Normal. | `test_cf_005_01_la_venta_descuenta_segun_la_receta` | Pasa |
| CF-005-02 | Ventas: registrar 3 Latte; abrir Inventario. | «Alerta de abastecimiento: CAF quedó en 196 (stock mínimo 200).» En Inventario, Café en grano 196 g en Reponer y nombrado en el cuadro amarillo. | `test_cf_005_02_el_cafe_queda_por_debajo_del_minimo` | Pasa |
| CF-005-03 | Ventas: registrar 1 Alfajor (queda 1 y el mínimo es 0); abrir Inventario. | «Alerta de abastecimiento: ALF quedó en 0 (stock mínimo 0).» En Inventario, Alfajor 0 und en Reponer y en el cuadro amarillo. | `test_cf_005_03_el_alfajor_queda_justo_en_el_minimo` | Pasa |
| CF-005-04 | Ventas: intentar 2 Alfajor y después registrar con todo en 0 (las dos salen en rojo); abrir Inventario. | Inventario muestra lo mismo que al abrir: Café en grano 250 g, Leche 2000 ml y Alfajor 1 und, en Normal. | `test_cf_005_04_las_ventas_rechazadas_no_cambian_el_inventario` | Pasa |
| CF-005-05 | Dos pestañas de Ventas con Alfajor = 1 y la casilla marcada; pulsar Registrar Venta en la primera y después en la segunda. | Primera: «Venta registrada por $4000 en efectivo.» Segunda: «Venta rechazada: Existencia insuficiente de ALF: hay 0 y se requieren 1.» Inventario: Alfajor 0 und, nunca −1. | `test_cf_005_05_dos_cajas_venden_el_ultimo_alfajor` | Pasa |
| CF-005-06 | Ventas: registrar 10 Latte; reiniciar; registrar 11 Latte y abrir Inventario. | Con 10 se registra y salen las alertas de CAF en 70 y de LEC en 0. Con 11: «Venta rechazada: Existencia insuficiente de LEC: hay 2000 y se requieren 2200.» e Inventario sigue en 250 g de café y 2000 ml de leche. | `test_cf_005_06_la_leche_alcanza_para_10_latte_y_no_para_11` | Pasa |
| CF-005-07 | Ventas: registrar 3 Latte y después 1 Alfajor; abrir Inventario. | Cuadro amarillo «Insumos en el stock mínimo o por debajo: Café en grano, Alfajor.» Leche 1400 ml en Normal. | `test_cf_005_07_insumos_por_reponer` | Pasa |
| CF-005-08 | Inventario: buscar cómo cambiar a mano la existencia del café. | No hay campos, botones ni formularios: la tabla solo se lee, y la nota dice que la existencia cambia con cada venta y cada lote aceptado. | `test_cf_005_08_la_existencia_no_se_puede_cambiar_a_mano` | Pasa |
| CF-007-01 | Recepción: llenar el lote base (Tabla 3) y pulsar Registrar recepción; abrir Inventario. | Mensaje verde «Lote L-101 aceptado: entran 5000 ml de Leche.» En Inventario, Leche 7000 ml. | `test_cf_007_01_lote_de_leche_valido` | Pasa |
| CF-007-02 | Ventas: 3 Latte. Recepción: Café en grano, 1000, g, lote C-55, factura FE-2302, sin fecha ni temperatura. | «Lote C-55 aceptado: entran 1000 g de Café en grano.» En Inventario, Café en grano pasa de 196 g en Reponer a 1196 g en Normal. | `test_cf_007_02_lote_de_cafe_sin_vencimiento_ni_temperatura` | Pasa |
| CF-007-03 | Recepción: lote base con Fecha de vencimiento dentro de 5 días y Temperatura 8.0. | «Lote L-101 aceptado: entran 5000 ml de Leche.» Los dos valores están justo en el límite permitido. | `test_cf_007_03_limites_que_se_aceptan` | Pasa |
| CF-007-04 | Recepción: lote base sin Proveedor (NIT y nombre); después, sin Número de factura. | «Recepción no registrada: Falta el dato obligatorio "Proveedor" de la recepción.» y lo mismo con "Número de factura". Leche sigue en 2000 ml. | `test_cf_007_04_sin_proveedor_o_sin_factura` | Pasa |
| CF-007-05 | Recepción: lote base sin Número de lote, sin Fecha de vencimiento o sin Temperatura. | Un mensaje rojo por campo, por ejemplo «Recepción no registrada: Dato inválido en "Temperatura": es obligatoria.» Leche sigue en 2000 ml. | `test_cf_007_05_campos_vacios_del_lote` | Pasa |
| CF-007-06 | Recepción: lote base con Cantidad 0 y después con -1. | «Recepción no registrada: Dato inválido en "Cantidad": debe ser mayor que cero.» Leche sigue en 2000 ml. | `test_cf_007_06_cantidad_cero_o_negativa` | Pasa |
| CF-007-07 | Recepción: registrar el lote base dos veces. | El segundo: «Recepción no registrada: Dato inválido en "Número de lote": ya se registró con esta factura.» Leche queda en 7000 ml, no en 12000. | `test_cf_007_07_el_mismo_lote_dos_veces` | Pasa |
| CF-007-08 | Recepción: lote base a 8.1 °C; después, el lote L-102 que vence dentro de 4 días. | «Lote L-101 rechazado: llegó a 8.1 °C y el máximo es 8 °C.» y «Lote L-102 rechazado: le quedan 4 días y el mínimo es 5.» Los dos quedan en Lotes pendientes de devolución y Leche sigue en 2000 ml. | `test_cf_007_08_limites_que_se_rechazan` | Pasa |
| CF-007-09 | Recepción: registrar el lote base y después el lote L-102 a 25.5 °C. | Lotes pendientes de devolución muestra solo L-102 · Leche · 5000 ml · Lácteos del Oriente · FE-2301 · llegó a 25.5 °C y el máximo es 8 °C. | `test_cf_007_09_lotes_pendientes_de_devolucion` | Pasa |
| CF-007-10 | Recepción: lote base con Unidad g. | «Recepción no registrada: Dato inválido en "Unidad": este insumo se controla en ml.» Leche sigue en 2000 ml. | `test_cf_007_10_unidad_que_no_corresponde_al_insumo` | Pasa |

## Lo que no se prueba con caja negra

Lo que pasa si no se puede guardar no tiene un botón en la pantalla. Lo cubren las
pruebas estructurales del RTF3, en `tests/test_ventas.py` y `tests/test_recepcion.py`.
