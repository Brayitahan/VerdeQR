import psycopg2, psycopg2.extras
conn = psycopg2.connect("postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10", cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

fixes = [
    # UsoArbol
    "ALTER TABLE UsoArbol ADD COLUMN IF NOT EXISTS especie INTEGER",
    "ALTER TABLE UsoArbol ADD COLUMN IF NOT EXISTS nombre VARCHAR(200)",
    # DetalleUso - code expects many columns
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS uso INTEGER",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS dureza VARCHAR(100)",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS resistencia VARCHAR(100)",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS usofinal TEXT",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS partecomestible VARCHAR(100)",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS formaconsumo TEXT",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS valornutricional TEXT",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS parteutilizada VARCHAR(100)",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS preparacion TEXT",
    "ALTER TABLE DetalleUso ADD COLUMN IF NOT EXISTS enfermedadestratadas TEXT",
    # CuriosidadesArbol
    "ALTER TABLE CuriosidadesArbol ADD COLUMN IF NOT EXISTS especie INTEGER",
    "ALTER TABLE CuriosidadesArbol ADD COLUMN IF NOT EXISTS titulo VARCHAR(200)",
    # InteraccionesEcologicas
    "ALTER TABLE InteraccionesEcologicas ADD COLUMN IF NOT EXISTS especie INTEGER",
    "ALTER TABLE InteraccionesEcologicas ADD COLUMN IF NOT EXISTS tipointeraccion VARCHAR(200)",
    # MedidasArbol (empty table)
    "CREATE TABLE IF NOT EXISTS MedidasArbol (idmedida SERIAL PRIMARY KEY, idarbol INTEGER, altura NUMERIC, diametro NUMERIC, fechamedicion DATE, estado INTEGER DEFAULT 1)",
    # CodigoQR - ensure arbol column exists
    "ALTER TABLE CodigoQR ADD COLUMN IF NOT EXISTS idarbol INTEGER",
    # Sugerencias - add missing
    "ALTER TABLE Sugerencias ADD COLUMN IF NOT EXISTS idarbol INTEGER",
]

for cmd in fixes:
    try:
        cur.execute(cmd)
        conn.commit()
        print(f"OK: {cmd}")
    except Exception as e:
        conn.rollback()
        print(f"ERR: {cmd} -> {e}")

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usoarbol' ORDER BY ordinal_position")
print(f"\nUsoArbol: {[r['column_name'] for r in cur.fetchall()]}")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'detalleuso' ORDER BY ordinal_position")
print(f"DetalleUso: {[r['column_name'] for r in cur.fetchall()]}")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'curiosidadesarbol' ORDER BY ordinal_position")
print(f"CuriosidadesArbol: {[r['column_name'] for r in cur.fetchall()]}")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'interaccionesecologicas' ORDER BY ordinal_position")
print(f"InteraccionesEcologicas: {[r['column_name'] for r in cur.fetchall()]}")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'codigoqr' ORDER BY ordinal_position")
print(f"CodigoQR: {[r['column_name'] for r in cur.fetchall()]}")

# Set defaults
for t in ['usoarbol', 'detalleuso', 'curiosidadesarbol', 'interaccionesecologicas']:
    cur.execute(f"UPDATE {t} SET estado = 1 WHERE estado IS NULL")
conn.commit()
print("Defaults set")

cur.close()
conn.close()
print("DONE")
