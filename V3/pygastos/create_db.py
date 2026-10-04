import sqlite3
import json
# from typing import Dict

CONFIG_FILE_PATH = "config/config.json"
DB_PATH = "static/db.sqlite"

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create
config_file = open(CONFIG_FILE_PATH)
config_data = json.load(config_file)
for table_name in config_data["tables"].keys():
    create_table_command = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    create_table_command += "\n id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"

    for field in config_data["fields"]:
        if field['name'] == 'id':
            continue
        create_table_command += f",\n {field['name']} {field['sql_type']}"
        if field['not_null'] is True:
            create_table_command += " NOT NULL"
    # create_table_command = create_table_command.rstrip(",\n ")
    create_table_command += ");"
# """
# Example:
# CREATE TABLE IF NOT EXISTS personal (
#  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#  concept TEXT NOT NULL,
#  subconcept TEXT,
#  income BOOL NOT NULL,
#  value DECIMAL(8, 2) NOT NULL,
#  date DATE NOT NULL,
#  description TEXT
# );
# """
cursor.execute(create_table_command)

# # Insert test data
# test_data = [
#     ("CTAG", None, True, 1000, "2025-01-01", None),
#     ("Imprevistos", None, False, 123.45, "2025-31-31", "Descripción de prueba"),
# ]

# test_insert_command = "INSERT INTO personal (concept, subconcept, income, value, date, description)"
# test_insert_command += " VALUES (?, ?, ?, ?, ?, ?)"
# cursor.executemany(test_insert_command, test_data)

# # Save changes and close connection
# conn.commit()
conn.close()

print(f"DataBase created successfully: {DB_PATH}")

# Validate date:
"""
from datetime import datetime
# Función para validar fecha en formato YYYY-MM-DD
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Filtrar los datos que tienen una fecha válida
valid_data = [entry for entry in test_data if validate_date(entry[3])]
"""
