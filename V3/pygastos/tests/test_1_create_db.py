import pytest
import sqlite3
import json
import os
from libs.manage_db import TableHandler, DBHandler
from config import config as cfg
import os.path


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
    _delete_db_if_exists()


@pytest.fixture(scope="module")
def db_handler():
    """Instancia DBHandler"""
    return DBHandler(db_path=cfg.TESTS_DB_PATH, config_path=cfg.CONFIG_FILE_PATH)


def test_check_db_not_exist():
    assert os.path.exists(cfg.TESTS_DB_PATH) is False


def test_create_db(db_handler: DBHandler):
    db_handler._create_db()
    assert os.path.exists(cfg.TESTS_DB_PATH) is True


@pytest.fixture(scope="module")
def table_handler():
    """Instancia TableHandler para la tabla {cfg.TESTS_DB_TABLE_NAME}"""
    with open(cfg.CONFIG_FILE_PATH) as f:
        tables_config = json.load(f)
    return TableHandler(db_path=cfg.TESTS_DB_PATH, table_name=cfg.TESTS_DB_TABLE_NAME,
                        tables_config=tables_config)


def test_create_table(table_handler: TableHandler):
    table_handler._create_table_if_not_exists()
    assert os.path.exists(cfg.TESTS_DB_PATH) is True
    conn = sqlite3.connect(cfg.TESTS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{cfg.TESTS_DB_TABLE_NAME}';")
    # cursor.execute("SELECT count(*) ... AND name=?;", ("{cfg.TESTS_DB_TABLE_NAME}'",))
    table_exists = cursor.fetchone()
    conn.close()
    assert table_exists[0] == 1


def test_remove_table(table_handler: TableHandler):
    table_handler._delete_table()
    conn = sqlite3.connect(cfg.TESTS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{cfg.TESTS_DB_TABLE_NAME}';")
    table_exists = cursor.fetchone()
    conn.close()
    assert table_exists[0] == 0


def test_remove_db(db_handler: DBHandler):
    db_handler._delete_db()
    assert os.path.exists(cfg.TESTS_DB_PATH) is False
