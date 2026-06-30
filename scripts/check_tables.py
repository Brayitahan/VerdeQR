import psycopg2, psycopg2.extras
conn = psycopg2.connect("postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10", cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()
for t in ['usoarbol', 'detalleuso', 'curiosidadesarbol', 'interaccionesecologicas', 'medidasarbol']:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", (t,))
    cols = [r['column_name'] for r in cur.fetchall()]
    print(f"{t}: {cols}")
cur.close()
conn.close()
