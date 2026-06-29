from flask import g
import psycopg2
import psycopg2.extras
import os

DB_CONFIG = None


class CaseInsensitiveDictRow(dict):
    def __getitem__(self, key):
        if isinstance(key, str):
            try:
                return super().__getitem__(key)
            except KeyError:
                key_lower = key.lower()
                for k in self:
                    if k.lower() == key_lower:
                        return super().__getitem__(k)
                raise KeyError(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        if isinstance(key, str) and super().__contains__(key):
            return True
        try:
            self[key]
            return True
        except KeyError:
            return False


class CaseInsensitiveRealDictCursor(psycopg2.extras.RealDictCursor):
    def _convert_to_case_insensitive(self, row):
        if row is not None:
            return CaseInsensitiveDictRow(row)
        return None

    def fetchone(self):
        return self._convert_to_case_insensitive(super().fetchone())

    def fetchall(self):
        rows = super().fetchall()
        return [self._convert_to_case_insensitive(r) for r in rows]

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        rows = super().fetchmany(size)
        return [self._convert_to_case_insensitive(r) for r in rows]


class DictConnection(psycopg2.extensions.connection):
    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', CaseInsensitiveRealDictCursor)
        return super().cursor(*args, **kwargs)


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
        return psycopg2.connect(DB_CONFIG['dsn'], connection_factory=DictConnection)
    return psycopg2.connect(connection_factory=DictConnection, **DB_CONFIG)


def get_db():
    if 'db' not in g:
        if DB_CONFIG is None:
            init_db_config()
        if 'dsn' in DB_CONFIG:
            g.db = psycopg2.connect(DB_CONFIG['dsn'], connection_factory=DictConnection)
        else:
            g.db = psycopg2.connect(connection_factory=DictConnection, **DB_CONFIG)
    return g.db


def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
