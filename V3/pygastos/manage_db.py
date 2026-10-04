import sqlite3


def check_col_names() -> set:
    connection = sqlite3.connect('static/db.sqlite')
    cursor = connection.execute('select * from personal')
    names = set(map(lambda x: x[0], cursor.description))
    return names


check_col_names()
