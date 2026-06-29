from flask import g
import pg8000
import pg8000.native
import os

DB_CONFIG = None

class DictRow:
    def __init__(self, columns, values):
        self._columns = columns
        self._mapping = dict(zip(columns, values))

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._mapping[self._columns[key]]
        return self._mapping[key]

    def get(self, key, default=None):
        return self._mapping.get(key, default)

    def __contains__(self, key):
        return key in self._mapping


def _row_to_dict(row, cursor):
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.columns]
    return DictRow(columns, row)


def init_db_config():
    global DB_CONFIG
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        DB_CONFIG = {'dsn': database_url}
        return
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
        'database': os.environ.get('DB_NAME', 'VerdeQR'),
        'port': int(os.environ.get('DB_PORT', 5432)),
    }


def get_db_connection():
    if DB_CONFIG is None:
        init_db_config()
    if 'dsn' in DB_CONFIG:
        return pg8000.native.Connection(DB_CONFIG['dsn'])
    return pg8000.native.Connection(**DB_CONFIG)


def get_db():
    if 'db' not in g:
        if DB_CONFIG is None:
            init_db_config()
        if 'dsn' in DB_CONFIG:
            g.db = pg8000.native.Connection(DB_CONFIG['dsn'])
        else:
            g.db = pg8000.native.Connection(**DB_CONFIG)
    return g.db


def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
