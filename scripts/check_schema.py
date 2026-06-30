import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

# Show columns for Usuario
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'usuario' ORDER BY ordinal_position")
print("=== Usuario columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for Arbol
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'arbol' ORDER BY ordinal_position")
print("\n=== Arbol columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for Especie
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'especie' ORDER BY ordinal_position")
print("\n=== Especie columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for Centro
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'centro' ORDER BY ordinal_position")
print("\n=== Centro columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for TipoBosque
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tipobosque' ORDER BY ordinal_position")
print("\n=== TipoBosque columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for Sugerencias
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'sugerencias' ORDER BY ordinal_position")
print("\n=== Sugerencias columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

# Show columns for CodigoQR
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'codigoqr' ORDER BY ordinal_position")
print("\n=== CodigoQR columns ===")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")

cur.close()
conn.close()
