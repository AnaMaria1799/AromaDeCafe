# Aroma de Café

Sistema para registrar las ventas, controlar el inventario y recibir los insumos de
la cafetería Aroma de Café. Proyecto de aula de Ingeniería de Software II
(Institución Universitaria Pascual Bravo), Grupo 4.

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

## Verificación antes de cada commit

    python -m ruff format .
    python -m ruff check .
    python -m mypy
    python -m pytest

Las cuatro deben terminar sin errores. `pytest` muestra además la cobertura de
sentencias y de ramas.

## Equipo

- Ana María Urrea Martínez
- Cristina Mejía Sierra
- Juan José Bolívar Celada