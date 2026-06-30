import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

tables = ["TipoBosque", "Centro", "Especie", "Arbol", "UsoArbol", "DetalleUso", "CuriosidadesArbol", "InteraccionesEcologicas"]
for t in tables:
    cur.execute(f"SELECT COUNT(*) as c FROM {t}")
    r = cur.fetchone()
    print(f"{t}: {r['c']} registros")

cur.execute("SELECT a.idarbol, e.nombrevulgar FROM arbol a JOIN especie e ON a.idespecie = e.idespecie")
for r in cur.fetchall():
    print(f"  Árbol {r['idarbol']}: {r['nombrevulgar']}")

cur.close()
conn.close()
