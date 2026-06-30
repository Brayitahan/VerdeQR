import psycopg2, psycopg2.extras
conn = psycopg2.connect("postgresql://postgres:ERYZCryosPAllvzaUKgQSERlUpBoXPKo@reseau.proxy.rlwy.net:34771/railway?connect_timeout=10", cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

# Tree data: idarbol, descripcion, caracteristicas, serviciosecosistemicos, imagen
trees = [
    (1,
     "Ceiba pentandra, conocida como Ceiba o Bonga, es un árbol majestuoso de la familia Malvaceae. Alcanza hasta 70 metros de altura, con un tronco de hasta 3 metros de diámetro. Su copa es amplia y extendida, proporcionando sombra a grandes extensiones. Es considerado sagrado en muchas culturas precolombinas, especialmente la maya, donde se le conocía como Yaxche o 'Árbol del Mundo'.",
     "Tronco recto y cilíndrico con contrafuertes o aletones en la base que pueden alcanzar 5 metros de altura. Corteza grisácea con espinas cónicas cuando joven. Hojas digitadas con 5-9 folíolos. Flores blancas o rosadas que abren por la noche. Frutos en cápsulas elípticas de 15-20 cm que contienen semillas envueltas en fibra algodonosa. Copa amplia y redondeada que puede alcanzar 40 metros de diámetro.",
     "Proporciona sombra y refugio a numerosas especies de aves, mamíferos y epífitas. Sus flores nocturnas alimentan murciélagos y polinizadores. La hojarasca enriquece el suelo con nutrientes. Captura grandes cantidades de CO₂. Regula el microclima en zonas urbanas y rurales. Previene la erosión del suelo con su extenso sistema radicular.",
     "css/js/img/20250703163348_Ceiba.jpg"),
    (2,
     "Handroanthus chrysanthus, popularmente conocido como Guayacán Amarillo, es un árbol de la familia Bignoniaceae. Es famoso por su espectacular floración amarilla que ocurre en la temporada seca, cuando el árbol pierde todas sus hojas y se cubre completamente de flores, creando uno de los espectáculos naturales más impresionantes de los trópicos.",
     "Árbol de tamaño mediano, alcanza 20-30 metros de altura. Tronco recto con corteza grisácea y fisurada. Madera extremadamente dura y pesada (densidad >1 g/cm³), considerada una de las maderas más duras de América. Hojas digitadas con 5 folíolos. Flores amarillo intenso en grandes racimos terminales. Frutos en cápsulas alargadas con semillas aladas.",
     "Su madera es apreciada para construcción pesada y muebles finos. Es un árbol ornamental de primer orden en parques y avenidas. Sus flores son fuente de néctar para abejas y mariposas. Proporciona sombra en espacios públicos. Ayuda a la conservación del suelo. Es un indicador natural de cambios estacionales en los ecosistemas secos.",
     "css/js/img/20250703162732_guayacan.jpg"),
    (3,
     "Quercus humboldtii, conocido como Roble Colombiano o Roble Negro, es la única especie de roble nativa de Colombia. Pertenece a la familia Fagaceae y es un árbol emblemático de los bosques andinos. Su nombre honra al naturalista alemán Alexander von Humboldt. Es considerado un símbolo de los ecosistemas de montaña colombianos.",
     "Árbol robusto que alcanza 25-35 metros de altura. Tronco recto de hasta 1.5 metros de diámetro. Corteza gruesa y fisurada de color gris oscuro. Hojas simples, alternas, coriáceas con bordes dentados. Flores masculinas en amentos colgantes. Frutos en bellotas ovoides de 2-3 cm. Madera de alta densidad, una de las más apreciadas del país. Crecimiento lento, tarda hasta 50 años en madurar.",
     "Especie clave para la restauración de bosques andinos. Sus bellotas son alimento esencial para roedores, aves y mamíferos. Sus ramas albergan una gran diversidad de aves rapaces y mamíferos arbóreos. Mejora la estructura del suelo con sus raíces profundas. Regula el ciclo hidrológico en cuencas de montaña. Captura y almacena grandes cantidades de carbono.",
     "css/js/img/20250703163648_roblea.jpg"),
    (4,
     "Ceroxylon quindiuense, la Palma de Cera del Quindío, es el árbol nacional de Colombia desde 1985. Es la palma más alta del mundo, alcanzando alturas excepcionales de hasta 60 metros. Crece exclusivamente en los bosques de niebla andinos entre los 2,000 y 3,000 metros de altitud, y es un símbolo de identidad nacional y de los paisajes del Eje Cafetero.",
     "Palma de porte erecto con estípite (tronco) cilíndrico, liso y cubierto de una capa de cera que le da su nombre. Anillos foliares visibles en todo el tronco. Hojas pinnadas de 4-6 metros de largo con folíolos dispuestos en planos diferentes. Inflorescencia interfoliar con flores pequeñas y numerosas. Frutos en drupas globosas de color rojo-anaranjado cuando maduros. Cera natural que protege contra la humedad y la radiación solar.",
     "Captura la niebla y regula la disponibilidad hídrica en los bosques de niebla. Proporciona hábitat para aves endémicas como el loro orejiamarillo. Sus frutos alimentan aves y mamíferos. Es un atractivo turístico y paisajístico fundamental en la región cafetera. Protege cuencas hidrográficas. Es un indicador de la salud de los ecosistemas de alta montaña andina.",
     "css/js/img/20250703161953_palma_cera.jpg"),
]

for t in trees:
    cur.execute("""
        UPDATE Arbol SET
            descripcion = %s,
            caracteristicas = %s,
            serviciosecosistemicos = %s,
            imagen = %s,
            imagenurl = %s
        WHERE idarbol = %s
    """, (t[1], t[2], t[3], t[4], t[4], t[0]))
    print(f"Tree {t[0]} updated")

conn.commit()

# Verify
cur.execute("SELECT idarbol, descripcion IS NOT NULL as has_desc, caracteristicas IS NOT NULL as has_carac, serviciosecosistemicos IS NOT NULL as has_srv, imagen FROM Arbol ORDER BY idarbol")
for r in cur.fetchall():
    print(dict(r))

cur.close()
conn.close()
print("DONE")
