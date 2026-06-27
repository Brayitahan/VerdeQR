from flask import g
import pymysql
import os
import re

DB_CONFIG = None

def init_db_config():
    global DB_CONFIG
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        match = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
        if match:
            user, password, host, port, database = match.groups()
            DB_CONFIG = {
                'host': host,
                'user': user,
                'password': password,
                'database': database,
                'port': int(port),
                'cursorclass': pymysql.cursors.DictCursor
            }
            return
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'VerdeQR'),
        'cursorclass': pymysql.cursors.DictCursor
    }

def get_db_connection():
    if DB_CONFIG is None:
        init_db_config()
    return pymysql.connect(**DB_CONFIG)

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db

def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
