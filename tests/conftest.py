from unittest.mock import Mock, create_autospec

import pytest

from aroma_cafe.datos.repositorios import (
    RepositorioInventario,
    RepositorioRecepciones,
    RepositorioVentas,
)
from aroma_cafe.datos.unidad_de_trabajo import UnidadDeTrabajo
from aroma_cafe.servicios.inventario import ServicioInventario


@pytest.fixture
def ventas_repo() -> Mock:
    return create_autospec(RepositorioVentas, instance=True)


@pytest.fixture
def inventario_repo() -> Mock:
    return create_autospec(RepositorioInventario, instance=True)


@pytest.fixture
def recepciones_repo() -> Mock:
    repositorio = create_autospec(RepositorioRecepciones, instance=True)
    repositorio.existe.return_value = False
    return repositorio


@pytest.fixture
def unidad(
    ventas_repo: Mock, inventario_repo: Mock, recepciones_repo: Mock
) -> UnidadDeTrabajo:
    return UnidadDeTrabajo(ventas_repo, inventario_repo, recepciones_repo)


@pytest.fixture
def inventario(unidad: UnidadDeTrabajo) -> ServicioInventario:
    return ServicioInventario(unidad)
