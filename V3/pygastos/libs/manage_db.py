import sys
import os
import json
import sqlite3
from typing import Dict
import logging

# Si el script se ejecuta directamente, ajusta sys.path para encontrar config
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import config as cfg


class TableHandler:
    def __init__(self, db_path: str, table_name: str, tables_config: dict):
        self._logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("log_file.log", 'w', 'utf-8'),
                logging.StreamHandler()
            ]
        )
        self._db_path = db_path
        self._table_name = table_name
        self._tables_config = tables_config
        self._table_fields = tables_config["fields"]
        self._table_fields_names = [field["name"] for field in self._table_fields]
        self._table_concepts = tables_config["tables"][table_name]["concepts"]
        self._table_concepts_names = [concept["name"] for concept in self._table_concepts]
        self._table_subconcepts = tables_config["tables"][table_name]["subconcepts"]

    # PUBLIC

    def create_table(self):
        self._create_table_if_not_exists()
        self._table_has_correct_fields()

    def add_row_to_table(self, **input_data) -> bool:
        input_fields_names = input_data.keys()
        result = self._input_fields_are_valid(input_fields_names=input_fields_names)
        if result is False:
            return False

        result = self._all_not_null_fields_are_input(input_fields_names=input_fields_names)
        if result is False:
            return False

        result = self._all_values_are_valid(input_data=input_data)
        if result is False:
            return False

        conn = self._connect()
        cursor = conn.cursor()
        columns = ', '.join(input_data.keys())
        placeholders = ', '.join(['?'] * len(input_data))
        query = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(input_data.values()))
        conn.commit()
        conn.close()

        return self._check_last_row(**input_data)

    # PRIVATE:

    def _connect(self):
        return sqlite3.connect(self._db_path)

    def _create_table_if_not_exists(self):
        conn = self._connect()
        create_table_command = f"CREATE TABLE IF NOT EXISTS {self._table_name} ("
        # create_table_command += "\n id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
        for table_field in self._table_fields:
            create_table_command += f"{table_field['name']} {table_field['sql_type']}"
            if table_field['not_null'] is True:
                create_table_command += " NOT NULL"
            if table_field['primary_key'] is True:
                create_table_command += " PRIMARY KEY"
            if table_field['autoincrement'] is True:
                create_table_command += " AUTOINCREMENT"
            create_table_command += ",\n "
        create_table_command = create_table_command.rstrip(",\n ")
        create_table_command += ");"
        cursor = conn.cursor()
        cursor.execute(create_table_command)
        conn.commit()
        conn.close()

    def _delete_table(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {self._table_name};")
        conn.commit()
        conn.close()
        conn.close()

    def _table_has_correct_fields(self):
        """Verifica que la estructura de la tabla en la BD coincida con config.json."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self._table_name})")
        db_columns = {row[1] for row in cursor.fetchall()}  # row[1] es el nombre de la columna

        expected_columns = set(self._table_fields_names)
        expected_columns.add('id')

        if db_columns != expected_columns:
            raise ValueError(
                f"Error: La estructura de la tabla '{self._table_name}' no coincide con config.json.\n"
                f"Esperado: {expected_columns}\n"
                f"Encontrado: {db_columns}"
            )

    def remove_table(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {self._table_name};")
        conn.close()

    def _get_col_names(self) -> list:
        conn = self._connect()
        cursor = conn.execute(f'select * from {self._table_name}')
        names = list(map(lambda x: x[0], cursor.description))
        conn.close()
        return names

    def _input_fields_are_valid(self, input_fields_names) -> bool:
        """Check all {input_fields_names} are DB table fields."""
        for input_field_name in input_fields_names:
            result = self._input_field_is_valid(input_field_name=input_field_name)
            if result is False:
                return False
        return True

    def _input_field_is_valid(self, input_field_name) -> bool:
        """Check {input_field_name} is a DB table field."""
        if input_field_name in self._table_fields_names:
            return True
        return False

    def _all_not_null_fields_are_input(self, input_fields_names) -> bool:
        """Check all not fields are present in the input fields."""
        for table_field in self._table_fields:
            if table_field['not_null'] is True and table_field['autoincrement'] is False\
                    and table_field['name'] not in input_fields_names:
                return False
        return True

    def _get_last_row(self):
        conn = self._connect()
        cursor = conn.cursor()
        # Suponiendo que "id" es la columna que aumenta con cada nuevo registro
        query = f"SELECT * FROM {self._table_name} ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()  # Devuelve solo una fila
        conn.close()
        return row

    def _check_last_row(self, **input_data) -> bool:
        row = self._get_last_row()
        row_dict = dict(zip(self._table_fields_names, row))
        for field in row_dict.keys():
            if field == 'id':
                continue
            if row_dict[field] is None:
                if field not in input_data or input_data[field] is None:
                    continue
                self._logger.error(f"Last row check failed. The field {field} is 'None' in DB"
                                   f" but is '{input_data[field]}' in input data.")
                return False
            if field not in input_data:
                self._logger.error(f"Last row check failed. The field {field} is '{row_dict[field]}' in DB"
                                   " but is not present in input data.")
                return False
            if input_data[field] != row_dict[field]:
                self._logger.error(f"Last row check failed. The field {field} is '{row_dict[field]}' in DB"
                                   f" but is '{input_data[field]}' in input data.")
                return False
        return True

    def _all_values_are_valid(self, input_data) -> bool:
        return True  # TODO:

    #     for table_field in self._table_fields:
    #         if table_field['name'] == input_field_name:
    #             break
    #     else:
    #         return False

    #     if table_field['sql_type'] == 'TEXT' and type(value) is not str:
    #         return False
    #     elif table_field['sql_type'] == 'BOOL' and type(value) is not bool:
    #         return False
    #     elif table_field['sql_type'].startswith('DECIMAL(') and type(value) is not int and type(value) is not float:
    #         return False
    #     elif table_field['sql_type'] == 'DATE':
    #         pass  # TODO:

    # def _concept_exists(self, input_concept_name) -> bool:
    #     if input_concept_name in self._table_concepts_names:
    #         return True
    #     return False


class DBHandler:
    def __init__(self, db_path: str, config_path: str):
        # TODO: Create db with tables if not exists.
        # self._db_path = cfg.CONFIG_DB_PATH

        self._conn = None  # Inicialmente, la conexión no está abierta
        self._db_path = db_path
        config_file = open(config_path)
        tables_config = json.load(config_file)
        tables_names = [table_name for table_name in tables_config["tables"].keys()]
        self._tables: Dict[str, TableHandler] = dict()
        for table_name in tables_names:
            self._tables[table_name] = TableHandler(
                db_path=db_path,
                table_name=table_name,
                tables_config=tables_config)

    def _create_db(self):
        # with sqlite3.connect(self._db_path) as conn:
        #     conn.execute("PRAGMA user_version = 1")
        #     pass
        #     # return
        self._conn = sqlite3.connect(self._db_path)
        self._conn.close()

    def _delete_db(self):
        if os.path.exists(self._db_path):
            os.remove(self._db_path)


db_handler = DBHandler(db_path=cfg.CONFIG_DB_PATH, config_path=cfg.CONFIG_FILE_PATH)


# print(db_handler._tables)
# print(db_handler._tables['personal']._table_concepts)
# input_data = {
#     "concept": "Gasolina",
#     "income": False,
#     "value": 12.35,
#     "date": "2025/01/31",
#     "description": "La descripción",
#     # "subconcept": None
# }
# input_data2 = {
#     "concept": "Gasolina",
#     "income": False,
#     "value": 12.35,
#     "date": "2025/01/31",
#     "subconcept": "abc"
# }
# ret = db_handler._tables['personal'].add_row_to_table(
#     **input_data
# )
# print(ret)
# ret = db_handler._tables['personal']._check_last_row(
#     **input_data2
# )
# print(ret)
