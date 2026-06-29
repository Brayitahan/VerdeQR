import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect("postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10")
cur = conn.cursor()

cur.execute("INSERT INTO Rol (NombreRol) VALUES ('Administrador') ON CONFLICT (NombreRol) DO NOTHING")
cur.execute("INSERT INTO Rol (NombreRol) VALUES ('Visitante') ON CONFLICT (NombreRol) DO NOTHING")

pw = generate_password_hash("verdeqr_admin_2026")
cur.execute(
    "INSERT INTO Usuario (Nombre, CorreoElectronico, Contrasena, Activo) VALUES (%s, %s, %s, TRUE) ON CONFLICT (CorreoElectronico) DO NOTHING",
    ("Admin VerdeQR", "jhon123@gmail.com", pw)
)

cur.execute("SELECT IDUsuario FROM Usuario WHERE CorreoElectronico = 'jhon123@gmail.com'")
uid = cur.fetchone()
if uid:
    cur.execute("SELECT IDRol FROM Rol WHERE NombreRol = 'Administrador'")
    rid = cur.fetchone()
    if rid:
        cur.execute("INSERT INTO UsuarioRol (IDUsuario, IDRol) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid[0], rid[0]))

pw2 = generate_password_hash("visitante123")
cur.execute(
    "INSERT INTO Usuario (Nombre, CorreoElectronico, Contrasena, Activo) VALUES (%s, %s, %s, TRUE) ON CONFLICT (CorreoElectronico) DO NOTHING",
    ("Visitante Prueba", "visitante@test.com", pw2)
)

cur.execute("SELECT IDUsuario FROM Usuario WHERE CorreoElectronico = 'visitante@test.com'")
uid2 = cur.fetchone()
if uid2:
    cur.execute("SELECT IDRol FROM Rol WHERE NombreRol = 'Visitante'")
    rid2 = cur.fetchone()
    if rid2:
        cur.execute("INSERT INTO UsuarioRol (IDUsuario, IDRol) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid2[0], rid2[0]))

for b in ["Bosque Seco Tropical", "Bosque Húmedo Tropical", "Bosque de Montaña", "Bosque de Galería"]:
    cur.execute("INSERT INTO TipoBosque (Descripcion) VALUES (%s) ON CONFLICT DO NOTHING", (b,))

conn.commit()
cur.close()
conn.close()
print("SEED DATA INSERTED OK")
