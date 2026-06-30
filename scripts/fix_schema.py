import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

# Add missing columns to Arbol (PostgreSQL folds unquoted names to lowercase)
alter_commands = [
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS especie INTEGER REFERENCES Especie(idespecie)",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS centro INTEGER REFERENCES Centro(idcentro)",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS tipobosque INTEGER REFERENCES TipoBosque(idtipobosque)",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS estado INTEGER",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS serviciosecosistemicos TEXT",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS caracteristicas TEXT",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS descripcion TEXT",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS imagen TEXT",
    "ALTER TABLE Arbol ADD COLUMN IF NOT EXISTS direccion TEXT",
    "ALTER TABLE Centro ADD COLUMN IF NOT EXISTS direccion TEXT",
    "ALTER TABLE Centro ADD COLUMN IF NOT EXISTS estado INTEGER DEFAULT 1",
]

for cmd in alter_commands:
    try:
        cur.execute(cmd)
        conn.commit()
        print(f"OK: {cmd}")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {cmd} -> {e}")

# Show Arbol columns
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'arbol' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  {row['column_name']} ({row['data_type']})")

cur.close()
conn.close()
print("SCHEMA FIX COMPLETE")
