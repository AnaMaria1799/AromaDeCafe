# Casos de prueba · Sprint 3

Cada caso une un criterio de aceptación con la prueba automática que lo revisa. Las pruebas se corren con `python -m pytest` y en GitHub Actions. Resultado actual: 118 pruebas pasan, con 100 % de cobertura.

## HU-005 · Actualizar existencias después de una venta (CAFE-13)

| ID | Criterio de aceptación | Datos de entrada | Resultado esperado | Prueba automática | Resultado |
|---|---|---|---|---|---|
| CP-005-01 | Al confirmarse la venta se descuenta lo que consume según la receta | Café 100 g, consumo 18 g | Queda en 82 g | `test_inventario.py::test_c2_descuenta_y_registra_la_salida_sin_alerta` | Pasa |
| CP-005-02 | El descuento se confirma o se revierte junto con la venta | Latte con 100 g de café y 1000 ml de leche; falla el guardado de la leche | No queda nada a medias: el café sigue en 100 g y no hay venta | `test_ventas.py::test_si_falla_el_descuento_del_segundo_insumo_no_queda_nada_a_medias` | Pasa |
| CP-005-03 | Cada descuento genera una salida asociada a la venta | Consumo de 18 g de café en una venta de Ana | Se registra una salida con la venta | `test_inventario.py::test_c2_descuenta_y_registra_la_salida_sin_alerta` | Pasa |
| CP-005-04 | Alerta si la existencia queda en el stock mínimo o por debajo (RN006) | Mínimo 20; queda en 21, 20 y 19 | Sin alerta con 21; alerta con 20 y con 19 | `test_inventario.py::test_c3_alerta_si_queda_en_el_stock_minimo_o_por_debajo` | Pasa |
| CP-005-05 | Antes de descontar se revalida la existencia | Existencia 0, cantidad 1 | Lanza ExistenciaInsuficienteError y no guarda nada | `test_inventario.py::test_c4_si_ya_no_alcanza_lanza_error_y_no_escribe` | Pasa |
| CP-005-06 | Sin consumos no se modifica nada | Consumos vacíos | No descuenta ni registra salidas | `test_inventario.py::test_c1_sin_consumos_no_descuenta_ni_registra` | Pasa |
| CP-005-07 | Si falla el guardado se revierte todo | El guardado de la venta lanza PersistenciaError | Se revierten la venta y el descuento | `test_ventas.py::test_c6_si_falla_el_guardado_se_revierte_todo` | Pasa |
| CP-005-08 | La actualización se ve de inmediato en el inventario | Café 100 g y leche 1000 ml; venta de 18 g y 200 ml | `existencias()` muestra 82 g y 800 ml | `test_existencias.py::test_despues_de_una_venta_se_ve_la_existencia_actualizada` | Pasa |

## HU-007 · Registrar la recepción de insumos (CAFE-5)

| ID | Criterio de aceptación | Datos de entrada | Resultado esperado | Prueba automática | Resultado |
|---|---|---|---|---|---|
| CP-007-01 | Registra cantidad, unidad, lote y fecha de vencimiento | Lote L-101: 5000 ml de leche, vence en 10 días, 4.0 °C | Se guarda con esos datos y queda aceptado | `test_recepcion.py::test_c5_lote_valido_se_guarda_aceptado_y_suma_existencias` | Pasa |
| CP-007-02 | Al aceptar el lote, suma a las existencias | Leche 1000 ml más el lote de 5000 ml | Queda en 6000 ml y se registra la entrada | `test_recepcion.py::test_c5_lote_valido_se_guarda_aceptado_y_suma_existencias` | Pasa |
| CP-007-03 | No se registra sin proveedor ni factura | Sin proveedor; o sin factura | Lanza IdentificacionIncompletaError con el campo que falta | `test_recepcion.py::test_c1_falta_proveedor_o_factura` | Pasa |
| CP-007-04 | Se validan los datos del lote | Sin número de lote, cantidad 0 o -1, unidad distinta, sin fecha o sin temperatura | Lanza DatosLoteInvalidosError con el campo | `test_dominio_recepcion.py::test_datos_invalidos_rn008` | Pasa |
| CP-007-05 | Un lote no se repite con la misma factura | Lote L-101 ya registrado con la factura FE-2301 | Lanza DatosLoteInvalidosError | `test_recepcion.py::test_c2_lote_repetido_con_la_misma_factura` | Pasa |
| CP-007-06 | Cada error indica el campo y no guarda | Recepción sin proveedor | La consola dice «Recepción no registrada: Falta el dato obligatorio 'proveedor' de la recepción.» | `test_consola.py::test_recepcion_no_registrada_muestra_el_campo` | Pasa |
| CP-007-07 | Un lote con poca vida útil o sobre la temperatura máxima se rechaza con su motivo | 25.5 °C con máximo 8; o vence en 4 días con mínimo 5 | Queda rechazado con su motivo y no suma existencias | `test_recepcion.py::test_c3_lote_fuera_de_condiciones_se_guarda_rechazado_y_no_suma` | Pasa |
| CP-007-08 | Límites de la RN008 | 5 y 4 días; 8 y 8.1 °C | Se aceptan 5 días y 8 °C; se rechazan 4 días y 8.1 °C | `test_dominio_recepcion.py::test_condiciones_del_lote_rn008` | Pasa |
| CP-007-09 | Si falla el guardado se revierten la recepción y la entrada | El guardado de la recepción lanza PersistenciaError | Se revierten los tres repositorios | `test_recepcion.py::test_c4_si_falla_el_guardado_se_revierten_recepcion_y_entrada` | Pasa |
| CP-007-10 | Todo lote rechazado queda pendiente de devolución (REQ-19) | Un lote bueno y uno a 25.5 °C | `lotes_por_devolver()` devuelve solo el rechazado | `test_lotes_por_devolver.py::test_solo_el_lote_rechazado_queda_por_devolver` | Pasa |
