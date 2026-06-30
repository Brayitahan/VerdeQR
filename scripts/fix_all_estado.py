import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

tables = [
    "Especie", "Centro", "UsoArbol", "DetalleUso",
    "CuriosidadesArbol", "InteraccionesEcologicas", "CodigoQR",
    "Sugerencias", "Arbol",
]

for t in tables:
    try:
        cur.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS estado INTEGER DEFAULT 1")
        conn.commit()
        print(f"OK: {t} +estado")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {t} -> {e}")

# Also add remaining Especie columns that the code references
for cmd in [
    "ALTER TABLE Especie ADD COLUMN IF NOT EXISTS nombrecientifico VARCHAR(100)",
    "ALTER TABLE Especie ADD COLUMN IF NOT EXISTS nombrevulgar VARCHAR(100)",
    "ALTER TABLE CodigoQR ADD COLUMN IF NOT EXISTS arbol INTEGER",
]:
    try:
        cur.execute(cmd)
        conn.commit()
        print(f"OK: {cmd}")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {cmd} -> {e}")

# Sync old column names
cur.execute("UPDATE Arbol SET estado = 1 WHERE estado IS NULL")
cur.execute("UPDATE Especie SET estado = 1 WHERE estado IS NULL")
cur.execute("UPDATE Centro SET estado = 1 WHERE estado IS NULL")
conn.commit()
print("Defaults set")

cur.close()
conn.close()
print("ALL ESTADO FIXES COMPLETE")
