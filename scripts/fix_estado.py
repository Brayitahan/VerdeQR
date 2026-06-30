import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

cur.execute("SELECT * FROM Estado")
rows = cur.fetchall()
print("Estado current:", rows)

# Add nombreestado column
cur.execute("ALTER TABLE Estado ADD COLUMN IF NOT EXISTS nombreestado VARCHAR(50)")
conn.commit()

# Seed default states
cur.execute("INSERT INTO Estado (nombreestado, descripcion) VALUES ('Activo', 'Registro activo') ON CONFLICT DO NOTHING")
cur.execute("INSERT INTO Estado (nombreestado, descripcion) VALUES ('Inactivo', 'Registro inactivo') ON CONFLICT DO NOTHING")
cur.execute("INSERT INTO Estado (nombreestado, descripcion) VALUES ('Bueno', 'Buen estado de salud') ON CONFLICT DO NOTHING")
cur.execute("INSERT INTO Estado (nombreestado, descripcion) VALUES ('Regular', 'Estado de salud regular') ON CONFLICT DO NOTHING")
cur.execute("INSERT INTO Estado (nombreestado, descripcion) VALUES ('Malo', 'Mal estado de salud') ON CONFLICT DO NOTHING")
conn.commit()

cur.execute("SELECT * FROM Estado")
for r in cur.fetchall():
    print(f"  ID={r['idestado']} nombre={r.get('nombreestado')} desc={r.get('descripcion')}")

cur.close()
conn.close()
print("ESTADO FIX COMPLETE")
