from datetime import date, timedelta
from decimal import Decimal

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.dominio.inventario import ArticuloInventario, UnidadMedida
from aroma_cafe.dominio.recepcion import LoteRecepcion, Proveedor
from aroma_cafe.dominio.ventas import (
    ItemPedido,
    LineaReceta,
    MedioPago,
    Pago,
    Pedido,
    Producto,
)
from aroma_cafe.interfaz import consola
from aroma_cafe.servicios.inventario import ServicioInventario
from aroma_cafe.servicios.recepcion import ServicioRecepcion
from aroma_cafe.servicios.ventas import ServicioVentas

CAFE = ArticuloInventario(
    "CAF", "Café en grano", UnidadMedida.GRAMO, Decimal(250), Decimal(200)
)
LECHE = ArticuloInventario(
    "LEC",
    "Leche",
    UnidadMedida.MILILITRO,
    Decimal(2000),
    Decimal(500),
    maneja_vencimiento=True,
    dias_minimos=5,
    temp_maxima=Decimal(8),
)
ALFAJOR = ArticuloInventario(
    "ALF", "Alfajor", UnidadMedida.UNIDAD, Decimal(1), Decimal(0)
)

LATTE = Producto(
    "LAT",
    "Latte",
    Decimal(6500),
    (LineaReceta("CAF", Decimal(18)), LineaReceta("LEC", Decimal(200))),
)
ALFAJOR_VENTA = Producto(
    "ALF", "Alfajor", Decimal(4000), (LineaReceta("ALF", Decimal(1)),)
)


def main() -> None:
    inventario_repo = RepositorioInventario([CAFE, LECHE, ALFAJOR])
    ventas_repo = RepositorioVentas()
    recepciones_repo = RepositorioRecepciones()
    unidad = UnidadDeTrabajo(ventas_repo, inventario_repo, recepciones_repo)
    inventario = ServicioInventario(unidad)
    ventas = ServicioVentas(inventario, unidad)
    recepcion = ServicioRecepcion(inventario, unidad)
    hoy = date.today()

    def mostrar_existencias(titulo: str) -> None:
        print(f"\n{titulo}")
        for codigo in ("CAF", "LEC", "ALF"):
            articulo = inventario_repo.obtener(codigo)
            print(f"  {articulo.nombre}: {articulo.existencia} {articulo.unidad.value}")

    def vender(titulo: str, items: list[ItemPedido], pago: Pago) -> None:
        print(f"\n{titulo}")
        print(consola.registrar_venta(ventas, Pedido(items), pago, "Ana"))

    def recibir(titulo: str, lote: LoteRecepcion) -> None:
        print(f"\n{titulo}")
        print(consola.registrar_recepcion(recepcion, lote, hoy))

    mostrar_existencias("EXISTENCIAS INICIALES")

    vender(
        "1. Venta válida: 2 lattes en efectivo",
        [ItemPedido(LATTE, 2)],
        Pago(MedioPago.EFECTIVO, confirmado=True),
    )
    vender(
        "2. Venta que deja existencias en el stock mínimo: 1 latte y 1 alfajor",
        [ItemPedido(LATTE, 1), ItemPedido(ALFAJOR_VENTA, 1)],
        Pago(MedioPago.TARJETA, confirmado=True),
    )
    vender(
        "3. Venta sin existencias: 2 alfajores",
        [ItemPedido(ALFAJOR_VENTA, 2)],
        Pago(MedioPago.EFECTIVO, confirmado=True),
    )
    vender(
        "4. Venta con el pago sin confirmar: 1 latte",
        [ItemPedido(LATTE, 1)],
        Pago(MedioPago.TRANSFERENCIA, confirmado=False),
    )

    proveedor = Proveedor("900123456-1", "Lácteos del Oriente")
    lote_leche = LoteRecepcion(
        "L-101",
        LECHE,
        Decimal(5000),
        UnidadMedida.MILILITRO,
        "Juan",
        proveedor,
        "FE-2301",
        hoy + timedelta(days=10),
        Decimal("4.0"),
    )
    recibir("5. Recepción válida: 5000 ml de leche a 4.0 °C", lote_leche)
    recibir(
        "6. Recepción fuera de temperatura: leche a 25.5 °C",
        LoteRecepcion(
            "L-102",
            LECHE,
            Decimal(5000),
            UnidadMedida.MILILITRO,
            "Juan",
            proveedor,
            "FE-2301",
            hoy + timedelta(days=10),
            Decimal("25.5"),
        ),
    )
    recibir(
        "7. Recepción sin factura electrónica: 1000 g de café",
        LoteRecepcion(
            "C-55", CAFE, Decimal(1000), UnidadMedida.GRAMO, "Juan", proveedor
        ),
    )

    mostrar_existencias("EXISTENCIAS FINALES")
    print(f"\nVentas en el historial: {len(ventas_repo.listar())}")
    print(f"Lotes registrados: {len(recepciones_repo.listar())}")
    print(f"Movimientos de inventario: {len(inventario_repo.movimientos())}")
