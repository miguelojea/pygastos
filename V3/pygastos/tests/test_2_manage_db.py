import pytest
import json
import os
from config import config as cfg
import os.path
import gc
import time
from libs.manage_db import TableHandler


def _delete_db_if_exists():
    """Delete the DB if it exists."""
    try:
        if os.path.exists(cfg.TESTS_DB_PATH):
            os.remove(cfg.TESTS_DB_PATH)
    except PermissionError as e:
        print(f"Error al eliminar la base de datos: {e}")


def setup_module(module):
    """Delete the DB before the tests."""
    _delete_db_if_exists()


def teardown_module(module):
    """Delete the DB after the tests."""
    gc.collect()  # Fuerza la recolección de basura para liberar recursos
    time.sleep(0.1)  # Breve pausa para asegurarse de que la conexión se libere
    _delete_db_if_exists()


@pytest.fixture(scope="module")
def table_handler():
    """Instancia TableHandler para la tabla {cfg.TESTS_DB_TABLE_NAME}"""
    with open(cfg.CONFIG_FILE_PATH) as f:
        tables_config = json.load(f)
    table_handler = TableHandler(db_path=cfg.TESTS_DB_PATH, table_name=cfg.TESTS_DB_TABLE_NAME,
                                 tables_config=tables_config)
    table_handler.create_table()
    return table_handler


def test_add_row_to_table_success(table_handler: TableHandler):
    """Add a valid row in the table."""
    result = table_handler.add_row_to_table(
        concept="Ocio",
        subconcept="Cine",
        income=False,
        value=20.50,
        date="2024-02-23",
        description="Entrada al cine"
    )
    assert result is True


def test_add_row_to_table_fail(table_handler: TableHandler):
    """Add a valid row in the table."""
    result = table_handler.add_row_to_table(
        Concept="Ocio",
        subconcept="Cine",
        income=False,
        value=20.50,
        date="2024-02-23",
        description="Entrada al cine"
    )
    assert result is False

# TODO: Group the test cases, maybe in folders. Use classes.
#       Check scopes: function (default), class, module, session.
