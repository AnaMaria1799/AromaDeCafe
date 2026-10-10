# Aroma de Café

Sistema para registrar las ventas, controlar el inventario y recibir los insumos de
la cafetería Aroma de Café. Proyecto de aula de Ingeniería de Software II
(Institución Universitaria Pascual Bravo), Grupo 4.

## Qué hace este incremento

| Historia de usuario | Qué hace el sistema | Método principal | Pruebas de sus caminos |
|---|---|---|---|
| HU-001 Registrar ventas | Registra la venta solo si el pedido tiene productos, las existencias alcanzan y el pago está confirmado con un medio habilitado | `ServicioVentas.registrar_venta` | `tests/test_ventas.py` (C1 a C7) |
| HU-005 Actualizar existencias después de una venta | Descuenta lo que consume cada venta según la receta y avisa cuando una existencia llega al stock mínimo | `ServicioInventario.descontar_por_venta` | `tests/test_inventario.py` (C1 a C4) |
| HU-007 Registrar la recepción de insumos | Acepta o rechaza cada lote según el proveedor, la factura, los datos, la vigencia y la temperatura | `ServicioRecepcion.registrar_recepcion` | `tests/test_recepcion.py` (C1 a C5) |

La venta y su descuento, igual que la recepción y su entrada, se guardan en una sola
operación: se confirman juntas o se revierten juntas.

Los datos se guardan en memoria. La base de datos relacional y la interfaz web del
diseño quedan para los incrementos siguientes.

## Estructura

    aroma_cafe/
    ├── dominio/     Reglas de negocio y excepciones
    ├── datos/       Repositorios en memoria y unidad de trabajo
    ├── servicios/   Un servicio por proceso: ventas, inventario y recepción
    └── interfaz/    Consola y demostración
    tests/           Pruebas unitarias, un archivo por servicio y por capa

Cada capa solo conoce a la que tiene debajo: la interfaz llama a los servicios, los
servicios usan el dominio y guardan a través de la capa de datos.

## Requisitos

- Python 3.10 o superior
- Git

## Instalación

    git clone https://github.com/AnaMaria1799/AromaDeCafe.git
    cd AromaDeCafe
    python -m venv .venv

Activa el entorno virtual con `.venv\Scripts\activate` en Windows o con
`source .venv/bin/activate` en macOS y Linux. Después instala las herramientas:

    python -m pip install -r requirements-dev.txt

## Ejecución

    python -m aroma_cafe

Recorre cuatro ventas y tres recepciones de ejemplo y muestra las existencias antes
y después.

## Pruebas y calidad

    python -m ruff format .
    python -m ruff check .
    python -m mypy
    python -m pytest
    python -m radon cc aroma_cafe -s

| Herramienta | Qué verifica |
|---|---|
| pytest y unittest.mock | Un caso por cada camino del diseño y por cada límite de sus condiciones; los repositorios se simulan para forzar la falla del guardado |
| coverage.py | Cobertura de sentencias y de ramas; la ejecución falla por debajo del 85 % |
| Ruff | Estilo, errores comunes, imports sin uso y complejidad máxima de 10 por función |
| mypy | Tipos en modo estricto |
| Radon | Complejidad ciclomática de cada método, para compararla con el diseño |

## Equipo

- Ana María Urrea Martínez
- Cristina Mejía Sierra
- Juan José Bolívar Celada