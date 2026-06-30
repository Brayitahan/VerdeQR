import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()
cur.execute("SELECT u.idusuario, u.nombre, u.correoelectronico, u.activo, STRING_AGG(r.nombrerol, ',') as roles FROM Usuario u LEFT JOIN UsuarioRol ur ON u.idusuario = ur.idusuario LEFT JOIN Rol r ON ur.idrol = r.idrol GROUP BY u.idusuario")
for row in cur.fetchall():
    print(f"ID={row['idusuario']} | {row['nombre']} | {row['correoelectronico']} | Activo={row['activo']} | Roles={row['roles']}")
cur.close()
conn.close()
