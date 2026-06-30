import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

fixes = [
    "ALTER TABLE TipoBosque ADD COLUMN IF NOT EXISTS nombre VARCHAR(100)",
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS estado INTEGER DEFAULT 1",
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS categoria TEXT",
]

for cmd in fixes:
    try:
        cur.execute(cmd)
        conn.commit()
        print(f"OK: {cmd}")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {cmd} -> {e}")

# Copy descripcion -> nombre for TipoBosque
cur.execute("UPDATE TipoBosque SET nombre = descripcion WHERE nombre IS NULL")
conn.commit()
print("Nombre copied from Descripcion")

# Show columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tipobosque'")
print("TipoBosque columns:", [r['column_name'] for r in cur.fetchall()])

cur.close()
conn.close()
print("FIX COMPLETE")
