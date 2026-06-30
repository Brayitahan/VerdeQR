import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

fixes = [
    # For sugerencias table - add columns the code expects
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS nombre VARCHAR(100)",
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS email VARCHAR(100)",
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS sugerencia TEXT",
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    # For CodigoQR table - add columns the code expects
    "ALTER TABLE CodigoQR ADD COLUMN IF NOT EXISTS nombrecientifico VARCHAR(100)",
    "ALTER TABLE CodigoQR ADD COLUMN IF NOT EXISTS nombrevulgar VARCHAR(100)",
    "ALTER TABLE CodigoQR ADD COLUMN IF NOT EXISTS idqr SERIAL",
    # For Especie - add IDTipoBosque column (used in queries)
    "ALTER TABLE Especie ADD COLUMN IF NOT EXISTS idtipobosque INTEGER",
    # For TokenRecuperacion
    "ALTER TABLE TokenRecuperacion ADD COLUMN IF NOT EXISTS idusuario INTEGER",
    "ALTER TABLE TokenRecuperacion ADD COLUMN IF NOT EXISTS usado BOOLEAN DEFAULT FALSE",
]

for cmd in fixes:
    try:
        cur.execute(cmd)
        conn.commit()
        print(f"OK: {cmd}")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {cmd} -> {e}")

# Sync data: copy idusuario -> usuario if needed
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tokenrecuperacion'")
cols = [r['column_name'] for r in cur.fetchall()]
print(f"TokenRecuperacion columns: {cols}")

# Also check if we need IDUsuario or usuario column
if 'idusuario' in cols:
    cur.execute("UPDATE TokenRecuperacion SET idusuario = \"IDUsuario\" WHERE idusuario IS NULL")
    conn.commit()
    print("Synced IDUsuario -> idusuario")

cur.close()
conn.close()
print("SUGERENCIAS FIX COMPLETE")
