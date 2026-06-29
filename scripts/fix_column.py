import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

cur.execute('ALTER TABLE Usuario RENAME COLUMN "Contrasena" TO "Contrase\u00f1a"')
print("OK columna renombrada")

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuario' ORDER BY ordinal_position")
for col in cur.fetchall():
    print(f"  Columna: {repr(col['column_name'])}")

cur.close()
conn.close()
