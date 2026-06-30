import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    "postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10",
    cursor_factory=psycopg2.extras.RealDictCursor
)
cur = conn.cursor()

# Clear existing data (safe for fresh DB)
cur.execute("DELETE FROM DetalleUso")
cur.execute("DELETE FROM UsoArbol")
cur.execute("DELETE FROM CuriosidadesArbol")
cur.execute("DELETE FROM InteraccionesEcologicas")
cur.execute("DELETE FROM CodigoQR")
cur.execute("DELETE FROM Arbol")
cur.execute("DELETE FROM EspecieCentro")
cur.execute("DELETE FROM Especie")
cur.execute("DELETE FROM Centro")
cur.execute("DELETE FROM TipoBosque WHERE descripcion NOT LIKE '%Ninguno%'")

# ============ TIPOS DE BOSQUE ============
for b in ["Bosque Seco Tropical", "Bosque Húmedo Tropical", "Bosque de Montaña", "Bosque de Galería"]:
    cur.execute("INSERT INTO TipoBosque (descripcion) VALUES (%s)", (b,))

# ============ CENTROS ============
cur.execute("INSERT INTO Centro (nombrecentro, direccion) VALUES ('Jardín Botánico de Medellín', 'Calle 73 # 51D-14, Medellín')")
cur.execute("INSERT INTO Centro (nombrecentro, direccion) VALUES ('Parque Nacional Natural Los Nevados', 'Manizales, Caldas')")
conn.commit()

# ============ ESPECIES ============
cur.execute("SELECT idtipobosque FROM tipobosque WHERE descripcion LIKE '%Húmedo%'")
bh = cur.fetchone()['idtipobosque']
cur.execute("SELECT idtipobosque FROM tipobosque WHERE descripcion LIKE '%Seco%'")
bs = cur.fetchone()['idtipobosque']
cur.execute("SELECT idtipobosque FROM tipobosque WHERE descripcion LIKE '%Montaña%'")
bm = cur.fetchone()['idtipobosque']

ceiba_desc = "Árbol sagrado y emblemático de la región tropical. Puede alcanzar hasta 70 m de altura."
guayacan_desc = "Árbol de gran belleza ornamental, famoso por su espectacular floración amarilla en temporada seca."
roble_desc = "Especie nativa emblemática de los bosques andinos colombianos."
palma_desc = "Árbol nacional de Colombia. Es la palma más alta del mundo, alcanzando hasta 60 m."

cur.execute("INSERT INTO Especie (nombrecientifico, nombrevulgar, descripcion, idtipobosque) VALUES ('Ceiba pentandra', 'Ceiba', %s, %s)", (ceiba_desc, bh))
cur.execute("INSERT INTO Especie (nombrecientifico, nombrevulgar, descripcion, idtipobosque) VALUES ('Handroanthus chrysanthus', 'Guayacán', %s, %s)", (guayacan_desc, bs))
cur.execute("INSERT INTO Especie (nombrecientifico, nombrevulgar, descripcion, idtipobosque) VALUES ('Quercus humboldtii', 'Roble Colombiano', %s, %s)", (roble_desc, bm))
cur.execute("INSERT INTO Especie (nombrecientifico, nombrevulgar, descripcion, idtipobosque) VALUES ('Ceroxylon quindiuense', 'Palma de Cera', %s, %s)", (palma_desc, bm))
conn.commit()

# ============ ÁRBOLES ============
cur.execute("SELECT idespecie FROM especie WHERE nombrevulgar = 'Ceiba'")
e1 = cur.fetchone()['idespecie']
cur.execute("SELECT idespecie FROM especie WHERE nombrevulgar = 'Guayacán'")
e2 = cur.fetchone()['idespecie']
cur.execute("SELECT idespecie FROM especie WHERE nombrevulgar = 'Roble Colombiano'")
e3 = cur.fetchone()['idespecie']
cur.execute("SELECT idespecie FROM especie WHERE nombrevulgar = 'Palma de Cera'")
e4 = cur.fetchone()['idespecie']
cur.execute("SELECT idcentro FROM centro ORDER BY idcentro LIMIT 1")
c1 = cur.fetchone()['idcentro']
cur.execute("SELECT idcentro FROM centro ORDER BY idcentro DESC LIMIT 1")
c2 = cur.fetchone()['idcentro']

cur.execute("""
    INSERT INTO Arbol (idespecie, idcentro, idtipobosque, latitud, longitud, altura, diametro, fechasiembra, estadosalud, notas, especie, centro, tipobosque, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
""", (e1, c1, bh, 6.251, -75.563, 45.0, 2.5, "2010-03-15", "Excelente", "Ceiba centenaria en el jardín botánico", e1, c1, bh))
cur.execute("""
    INSERT INTO Arbol (idespecie, idcentro, idtipobosque, latitud, longitud, altura, diametro, fechasiembra, estadosalud, notas, especie, centro, tipobosque, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
""", (e2, c1, bs, 6.252, -75.564, 22.0, 0.8, "2015-06-20", "Bueno", "Guayacán en floración", e2, c1, bs))
cur.execute("""
    INSERT INTO Arbol (idespecie, idcentro, idtipobosque, latitud, longitud, altura, diametro, fechasiembra, estadosalud, notas, especie, centro, tipobosque, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
""", (e3, c2, bm, 4.971, -75.303, 18.0, 0.6, "2018-01-10", "Bueno", "Roble en el parque natural", e3, c2, bm))
cur.execute("""
    INSERT INTO Arbol (idespecie, idcentro, idtipobosque, latitud, longitud, altura, diametro, fechasiembra, estadosalud, notas, especie, centro, tipobosque, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
""", (e4, c2, bm, 4.972, -75.304, 35.0, 0.5, "2012-11-05", "Regular", "Palma de cera en zona de protección", e4, c2, bm))
conn.commit()

# ============ USOS ============
categorias = [
    ("Maderable", "Madera de alta calidad para construcción y ebanistería"),
    ("Medicinal", "Propiedades curativas y medicinales"),
    ("Comestible", "Frutos y partes comestibles"),
    ("Ornamental", "Valor estético y ornamental"),
    ("RestauracionEcologica", "Especie clave para restauración de ecosistemas"),
    ("CulturalCeremonial", "Importancia cultural y ceremonial"),
    ("ProteccionAmbiental", "Protección de suelos y cuerpos de agua"),
    ("Aromatica", "Aceites esenciales y aromas naturales"),
    ("Artesanal", "Materia prima para artesanías"),
    ("Forrajero", "Alimento para ganado y fauna"),
    ("Sombra", "Proporciona sombra y regulación climática"),
    ("CercaViva", "Utilizada como cerca viva o barrera rompevientos"),
    ("Tinte", "Producción de tintes naturales"),
]
for cat, desc in categorias:
    cur.execute("INSERT INTO UsoArbol (categoria, descripcion) VALUES (%s, %s)", (cat, desc))
conn.commit()

cur.execute("SELECT idarbol FROM arbol ORDER BY idarbol")
a_ids = [r['idarbol'] for r in cur.fetchall()]
cur.execute("SELECT iduso FROM usoarbol ORDER BY iduso")
u_ids = [r['iduso'] for r in cur.fetchall()]

detalles = [
    (a_ids[0], u_ids[0], "Madera utilizada para carpintería y construcción de canoas"),
    (a_ids[0], u_ids[4], "Especie clave en proyectos de reforestación"),
    (a_ids[0], u_ids[5], "Árbol sagrado en varias culturas indígenas"),
    (a_ids[1], u_ids[0], "Madera extremadamente dura para muebles finos"),
    (a_ids[1], u_ids[3], "Árbol ornamental por su espectacular floración"),
    (a_ids[1], u_ids[10], "Excelente sombra en parques y avenidas"),
    (a_ids[2], u_ids[0], "Madera de alta calidad para construcción"),
    (a_ids[2], u_ids[4], "Especie clave para restauración de bosques andinos"),
    (a_ids[2], u_ids[9], "Sus bellotas son alimento para fauna silvestre"),
    (a_ids[3], u_ids[3], "Palma ornamental de gran valor paisajístico"),
    (a_ids[3], u_ids[5], "Árbol nacional y símbolo de identidad colombiana"),
    (a_ids[3], u_ids[6], "Protege cuencas hidrográficas en bosque de niebla"),
    (a_ids[0], u_ids[2], "Semillas comestibles después de procesamiento"),
]
for d in detalles:
    cur.execute("INSERT INTO DetalleUso (idarbol, iduso, descripcion) VALUES (%s, %s, %s)", d)
conn.commit()

# ============ CURIOSIDADES ============
curiosidades = [
    (a_ids[0], "El árbol de la vida", "La ceiba conecta el cielo y el inframundo en la mitología maya"),
    (a_ids[0], "Raíces tabulares", "Sus raíces pueden extenderse 5 m del tronco para dar estabilidad"),
    (a_ids[0], "Algodón de ceiba", "Sus frutos producen fibra algodonosa usada para rellenar almohadas"),
    (a_ids[0], "Hábitat de fauna", "Sus flores son fuente de néctar para murciélagos y aves"),
    (a_ids[0], "Longevidad", "Puede vivir más de 200 años en condiciones óptimas"),
    (a_ids[1], "Floración espectacular", "El guayacán se cubre completamente de flores amarillas"),
    (a_ids[1], "Madera de hierro", "Su madera es tan densa que se hunde en el agua"),
    (a_ids[1], "Indicador climático", "Florece en temporada seca, indicando cambios estacionales"),
    (a_ids[1], "Árbol urbano", "Muy utilizado en espacios públicos por su sombra y belleza"),
    (a_ids[2], "Roble andino", "Es la única especie de roble nativa de Colombia"),
    (a_ids[2], "Alimento silvestre", "Sus bellotas son alimento esencial para fauna"),
    (a_ids[2], "Crecimiento lento", "Tarda hasta 50 años en alcanzar su madurez"),
    (a_ids[3], "Árbol nacional", "Declarada árbol nacional de Colombia en 1985"),
    (a_ids[3], "La más alta del mundo", "Especie de palma más alta, hasta 60 metros"),
    (a_ids[3], "Cera vegetal", "Su tronco produce cera que protege contra la humedad"),
    (a_ids[3], "Bosque de niebla", "Crece exclusivamente en ecosistemas de bosque de niebla andino"),
    (a_ids[3], "En peligro crítico", "Clasificada como especie amenazada de extinción"),
    (a_ids[2], "Madera noble", "Una de las maderas más finas y apreciadas de Colombia"),
]
for c in curiosidades:
    cur.execute("INSERT INTO CuriosidadesArbol (idarbol, titulo, descripcion) VALUES (%s, %s, %s)", c)
conn.commit()

# ============ INTERACCIONES ECOLÓGICAS ============
interacciones = [
    (a_ids[0], "Polinización", "Murciélagos y abejas polinizan sus flores nocturnas"),
    (a_ids[0], "Dispersión", "El viento dispersa semillas envueltas en fibra algodonosa"),
    (a_ids[0], "Refugio", "Sus ramas albergan gran diversidad de epífitas"),
    (a_ids[0], "Nutrientes", "Hojarasca rica en nutrientes que fertiliza el suelo"),
    (a_ids[1], "Polinización", "Abejas y mariposas visitan flores durante floración masiva"),
    (a_ids[1], "Dispersión", "Semillas dispersadas por el viento (anemocoria)"),
    (a_ids[1], "Simbiosis", "Asociación con hongos micorrízicos para absorción de nutrientes"),
    (a_ids[2], "Alimento", "Bellotas son alimento principal para roedores y aves"),
    (a_ids[2], "Refugio", "Hábitat para aves rapaces y mamíferos arbóreos"),
    (a_ids[2], "Suelo", "Mejora la estructura del suelo con raíces profundas"),
    (a_ids[2], "Agua", "Regula el ciclo hidrológico en bosques de montaña"),
    (a_ids[3], "Polinización", "Polinizada por insectos especializados de alta montaña"),
    (a_ids[3], "Refugio", "Hojas albergan aves e insectos endémicos"),
    (a_ids[3], "Clima", "Captura niebla y regula la disponibilidad hídrica"),
]
for i in interacciones:
    cur.execute("INSERT INTO InteraccionesEcologicas (idarbol, tipointeraccion, descripcion) VALUES (%s, %s, %s)", i)
conn.commit()

print("TODOS LOS DATOS INSERTADOS CORRECTAMENTE")
cur.close()
conn.close()
