import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

cur.execute("SELECT idarbol, especie, idespecie, centro, idcentro, tipobosque, idtipobosque FROM arbol WHERE idarbol = 1")
r = cur.fetchone()
print("Row:", dict(r) if r else "NOT FOUND")

cur.execute("SELECT * FROM arbol ORDER BY idarbol")
for r in cur.fetchall():
    print(f"  idarbol={r['idarbol']} especie={r.get('especie')} idespecie={r.get('idespecie')} centro={r.get('centro')}")

cur.close()
conn.close()
