import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("DATABASE_URL no está configurada")
    exit(1)

print(f"Conectando a la base de datos...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()

with open('migracion_postgres.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

statements = [s.strip() for s in sql.split(';') if s.strip()]
success = 0
errors = 0

for stmt in statements:
    try:
        cur.execute(stmt + ';')
        success += 1
        print(f"OK {stmt[:70]}...")
    except Exception as e:
        if 'already exists' in str(e).lower():
            success += 1
            print(f"SKIP {stmt[:70]}... (ya existe)")
        else:
            errors += 1
            print(f"FAIL {stmt[:70]}... {e}")

cur.close()
conn.close()
print(f"\nOK: {success}, FAIL: {errors}")
