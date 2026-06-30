import psycopg2
import psycopg2.extras
conn = psycopg2.connect("postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10", cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tokenrecuperacion' ORDER BY ordinal_position")
for r in cur.fetchall():
    print(f"  {r['column_name']} ({r['data_type']})")
cur.close()
conn.close()
