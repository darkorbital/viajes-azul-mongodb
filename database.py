import os
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_db():
    global _client
    if _client is None:
        uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/viajes_azul")
        _client = MongoClient(uri)
    db_name = _client.get_default_database().name if "mongodb+srv" in os.environ.get("MONGODB_URI", "") else "viajes_azul"
    return _client[db_name]


def init_db():
    db = get_db()
    col = db.destinos

    if col.count_documents({}) > 0:
        return

    # ──────────────────────────────────────────────────────────────────────────
    # Diferencia clave vs SQLite:
    # En lugar de 5 tablas con claves foráneas, cada destino es un documento
    # que contiene arrays embebidos de paquetes, hoteles y valoraciones.
    # No hay JOINs: toda la información de un destino vive junta.
    # ──────────────────────────────────────────────────────────────────────────
    destinos = [
        # ── PLAYA ──────────────────────────────────────────────────────────
        {
            "id": 1, "nombre": "Cancún", "pais": "México", "continente": "América",
            "tipo": "playa", "precio_desde": 899,
            "imagen_url": "https://images.unsplash.com/photo-1510097467424-192d713fd8b2?w=800&h=500&fit=crop",
            "descripcion": "Paraíso caribeño de aguas turquesas y arena blanca. Cancún combina playas espectaculares, cultura maya milenaria y una vida nocturna vibrante que no para.",
            "valoracion": 4.7, "actividades": "snorkel,buceo,ruinas mayas,parasailing,vida nocturna",
            "clima": "Tropical húmedo", "mejor_epoca": "Diciembre – Abril",
            "paquetes": [
                {"nombre": "Cancún Todo Incluido", "precio": 1299, "duracion_dias": 7, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Vuelo + 7 noches en hotel 5★ todo incluido en la zona hotelera"},
                {"nombre": "Cancún + Ruinas Mayas", "precio": 1599, "duracion_dias": 10, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Paquete completo con excursión a Chichén Itzá y Tulum"},
                {"nombre": "Cancún Familiar", "precio": 1899, "duracion_dias": 8, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 4, "descripcion": "Paquete para 2 adultos + 2 niños con actividades para toda la familia"},
            ],
            "hoteles": [
                {"nombre": "Grand Hyatt Cancún", "categoria": 5, "precio_noche": 280, "descripcion": "Resort de lujo frente al mar con piscinas infinitas y spa", "servicios": "piscina infinita,spa,gym,5 restaurantes,kids club"},
                {"nombre": "Hotel Krystal Cancún", "categoria": 4, "precio_noche": 150, "descripcion": "Hotel 4★ en la zona hotelera con todo incluido disponible", "servicios": "piscina,restaurante,bar,animación"},
                {"nombre": "Ibis Cancún Centro", "categoria": 3, "precio_noche": 75, "descripcion": "Hotel económico y bien ubicado en el centro histórico", "servicios": "wifi,desayuno,parking"},
            ],
            "valoraciones": [
                {"usuario_nombre": "Ana García", "puntuacion": 5.0, "comentario": "Cancún es mágico. Las aguas turquesas y la arena blanca son increíbles. ¡Repetiremos!", "fecha": "2025-03-15"},
                {"usuario_nombre": "Carlos López", "puntuacion": 4.5, "comentario": "Hotel excelente, todo incluido de calidad. Las excursiones mayas son imprescindibles.", "fecha": "2025-02-20"},
            ],
        },
        {
            "id": 2, "nombre": "Bali", "pais": "Indonesia", "continente": "Asia",
            "tipo": "playa", "precio_desde": 1100,
            "imagen_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&h=500&fit=crop",
            "descripcion": "La isla de los dioses. Bali mezcla templos milenarios, terrazas de arroz, playas de ensueño y una espiritualidad única que transforma a todo viajero.",
            "valoracion": 4.8, "actividades": "surf,yoga,templos,spa,buceo,senderismo",
            "clima": "Tropical", "mejor_epoca": "Mayo – Septiembre",
            "paquetes": [
                {"nombre": "Bali Espiritual", "precio": 1450, "duracion_dias": 10, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Yoga retreat, templos sagrados y playas paradisíacas"},
                {"nombre": "Bali Surf & Relax", "precio": 1350, "duracion_dias": 8, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Clases de surf en Kuta + spa de lujo en Ubud"},
            ],
            "hoteles": [
                {"nombre": "Four Seasons Bali Jimbaran", "categoria": 5, "precio_noche": 650, "descripcion": "Villas privadas con piscina frente al Océano Índico", "servicios": "villas privadas,spa,yoga,2 piscinas,restaurante gourmet"},
                {"nombre": "Alaya Resort Ubud", "categoria": 4, "precio_noche": 180, "descripcion": "Hotel boutique en el corazón verde de Ubud", "servicios": "piscina,spa,clases cocina balinesa,ciclismo"},
            ],
            "valoraciones": [
                {"usuario_nombre": "María Fernández", "puntuacion": 5.0, "comentario": "Bali superó todas mis expectativas. Los templos, la comida, la gente... todo perfecto.", "fecha": "2025-04-01"},
                {"usuario_nombre": "Luis Martínez", "puntuacion": 4.8, "comentario": "Destino único en el mundo. La mezcla de playa, cultura y espiritualidad es irrepetible.", "fecha": "2025-01-10"},
            ],
        },
        {
            "id": 3, "nombre": "Maldivas", "pais": "Maldivas", "continente": "Asia",
            "tipo": "playa", "precio_desde": 2500,
            "imagen_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&h=500&fit=crop",
            "descripcion": "El destino más exclusivo del planeta. Bungalows sobre agua cristalina, arrecifes de coral vírgenes y puestas de sol que dejan sin palabras.",
            "valoracion": 4.9, "actividades": "snorkel,buceo,spa,kayak,pesca",
            "clima": "Tropical", "mejor_epoca": "Noviembre – Abril",
            "paquetes": [], "hoteles": [],
            "valoraciones": [
                {"usuario_nombre": "Sara González", "puntuacion": 5.0, "comentario": "Las Maldivas son el paraíso en la Tierra. Cada euro invertido valió la pena.", "fecha": "2025-03-28"},
            ],
        },
        {
            "id": 4, "nombre": "Tenerife", "pais": "España", "continente": "Europa",
            "tipo": "playa", "precio_desde": 450,
            "imagen_url": "https://images.unsplash.com/photo-1558618047-3a68c09f34d9?w=800&h=500&fit=crop",
            "descripcion": "La isla afortunada. Tenerife ofrece playas volcánicas únicas, el Teide nevado y un clima envidiable durante todo el año. ¡La escapada perfecta desde España!",
            "valoracion": 4.5, "actividades": "surf,senderismo,parques acuáticos,avistamiento ballenas",
            "clima": "Subtropical", "mejor_epoca": "Todo el año",
            "paquetes": [
                {"nombre": "Tenerife Fin de Semana", "precio": 299, "duracion_dias": 3, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Escapada de fin de semana con vuelo directo desde Madrid"},
                {"nombre": "Tenerife Semana Completa", "precio": 599, "duracion_dias": 7, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Una semana en el sur con acceso a los mejores parques acuáticos"},
            ],
            "hoteles": [
                {"nombre": "Hard Rock Hotel Tenerife", "categoria": 5, "precio_noche": 220, "descripcion": "El hotel más rockero de la isla con música en vivo", "servicios": "piscinas,spa,gym,música en vivo,kids club"},
                {"nombre": "Bahía del Duque", "categoria": 5, "precio_noche": 350, "descripcion": "Gran lujo en Costa Adeje con arquitectura canaria tradicional", "servicios": "playa privada,8 piscinas,11 restaurantes,spa"},
            ],
            "valoraciones": [
                {"usuario_nombre": "Ana García", "puntuacion": 4.5, "comentario": "Tenerife es perfecta para escapar del frío sin salir de España. El Teide impresiona.", "fecha": "2025-02-14"},
            ],
        },
        {
            "id": 5, "nombre": "Phuket", "pais": "Tailandia", "continente": "Asia",
            "tipo": "playa", "precio_desde": 850,
            "imagen_url": "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800&h=500&fit=crop",
            "descripcion": "La perla del Andaman. Playas de aguas cristalinas, templos budistas coloridos y la famosa vida nocturna de Patong hacen de Phuket un destino irresistible.",
            "valoracion": 4.6, "actividades": "buceo,snorkel,templos,vida nocturna,excursiones",
            "clima": "Tropical monzónico", "mejor_epoca": "Noviembre – Abril",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
        # ── MONTAÑA ────────────────────────────────────────────────────────
        {
            "id": 6, "nombre": "Zermatt", "pais": "Suiza", "continente": "Europa",
            "tipo": "montaña", "precio_desde": 1800,
            "imagen_url": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&h=500&fit=crop",
            "descripcion": "Al pie del mítico Matterhorn. Un pueblo sin coches rodeado de los Alpes suizos: esquí de alta montaña en invierno y senderismo épico en verano.",
            "valoracion": 4.8, "actividades": "esquí,snowboard,senderismo,alpinismo,spa",
            "clima": "Alpino", "mejor_epoca": "Dic – Mar / Jun – Sep",
            "paquetes": [
                {"nombre": "Ski Matterhorn Semana", "precio": 2200, "duracion_dias": 7, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Forfait de esquí + hotel alpino + cena de fondue incluida"},
            ],
            "hoteles": [],
            "valoraciones": [
                {"usuario_nombre": "Sara González", "puntuacion": 4.8, "comentario": "Zermatt con nieve es una postal viviente. Esquiar bajo el Matterhorn es experiencia única.", "fecha": "2025-01-25"},
            ],
        },
        {
            "id": 7, "nombre": "Patagonia", "pais": "Argentina / Chile", "continente": "América",
            "tipo": "montaña", "precio_desde": 1600,
            "imagen_url": "https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&h=500&fit=crop",
            "descripcion": "El fin del mundo. Glaciares, torres de granito, cóndores y un silencio que solo la naturaleza más salvaje puede ofrecer. Una experiencia transformadora.",
            "valoracion": 4.9, "actividades": "trekking,alpinismo,fauna,kayak glaciares",
            "clima": "Frío patagónico", "mejor_epoca": "Octubre – Marzo",
            "paquetes": [
                {"nombre": "Patagonia Salvaje 12 días", "precio": 2800, "duracion_dias": 12, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Trekking en Torres del Paine + glaciar Perito Moreno"},
            ],
            "hoteles": [], "valoraciones": [],
        },
        {
            "id": 8, "nombre": "Nepal – Everest Trek", "pais": "Nepal", "continente": "Asia",
            "tipo": "montaña", "precio_desde": 1200,
            "imagen_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&h=500&fit=crop",
            "descripcion": "El techo del mundo. El trekking al campo base del Everest es una odisea única: paisajes himalayos imponentes, cultura tibetana y una sensación de logro sin igual.",
            "valoracion": 4.7, "actividades": "trekking,escalada,cultura budista,aventura extrema",
            "clima": "Alpino de altitud", "mejor_epoca": "Mar – May / Sep – Nov",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
        {
            "id": 9, "nombre": "Banff", "pais": "Canadá", "continente": "América",
            "tipo": "montaña", "precio_desde": 1400,
            "imagen_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&h=500&fit=crop",
            "descripcion": "El corazón de las Rocosas canadienses. Lagos de color turquesa, osos grizzly, alces y montañas nevadas forman un espectáculo natural absolutamente incomparable.",
            "valoracion": 4.8, "actividades": "esquí,senderismo,kayak,fauna,fotografía naturaleza",
            "clima": "Continental", "mejor_epoca": "Jun – Ago / Dic – Mar",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
        # ── CIUDAD ─────────────────────────────────────────────────────────
        {
            "id": 10, "nombre": "París", "pais": "Francia", "continente": "Europa",
            "tipo": "ciudad", "precio_desde": 650,
            "imagen_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&h=500&fit=crop",
            "descripcion": "La ciudad de la luz. La Torre Eiffel, el Louvre, la gastronomía exquisita y ese ambiente romántico único hacen de París el destino más visitado del mundo.",
            "valoracion": 4.7, "actividades": "museos,gastronomía,moda,arquitectura,crucero Sena",
            "clima": "Oceánico", "mejor_epoca": "Abr – Jun / Sep – Oct",
            "paquetes": [
                {"nombre": "París Romántico", "precio": 799, "duracion_dias": 4, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Escapada romántica: cena en la Torre Eiffel + crucero por el Sena"},
                {"nombre": "París Cultural", "precio": 950, "duracion_dias": 5, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Visita los mejores museos: Louvre, Orsay y Pompidou con guía experto"},
            ],
            "hoteles": [
                {"nombre": "Le Bristol Paris", "categoria": 5, "precio_noche": 850, "descripcion": "El palace más emblemático de París junto a los Campos Elíseos", "servicios": "piscina,spa,restaurante 3★ Michelin,butler"},
                {"nombre": "Hotel du Louvre", "categoria": 4, "precio_noche": 320, "descripcion": "Histórico hotel a 2 minutos del Louvre con vistas a la Ópera", "servicios": "restaurante,bar,concierge,wifi"},
                {"nombre": "Ibis Paris Gare du Nord", "categoria": 3, "precio_noche": 95, "descripcion": "Hotel práctico bien comunicado con todo el centro", "servicios": "wifi,desayuno,24h recepción"},
            ],
            "valoraciones": [
                {"usuario_nombre": "Carlos López", "puntuacion": 4.7, "comentario": "París nunca defrauda. La cena en la Torre Eiffel fue absolutamente inolvidable.", "fecha": "2025-04-15"},
            ],
        },
        {
            "id": 11, "nombre": "Tokyo", "pais": "Japón", "continente": "Asia",
            "tipo": "ciudad", "precio_desde": 1200,
            "imagen_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=500&fit=crop",
            "descripcion": "El futuro ya está aquí. Tokyo es una ciudad de contrastes donde la tradición samurái convive con la tecnología más avanzada del mundo y la gastronomía más exquisita.",
            "valoracion": 4.8, "actividades": "gastronomía,templos,cultura,tecnología,anime,shopping",
            "clima": "Húmedo subtropical", "mejor_epoca": "Mar – May / Sep – Nov",
            "paquetes": [], "hoteles": [],
            "valoraciones": [
                {"usuario_nombre": "María Fernández", "puntuacion": 4.9, "comentario": "Tokyo es otro planeta. La organización, la comida, la cultura... impresionante.", "fecha": "2025-03-05"},
            ],
        },
        {
            "id": 12, "nombre": "Nueva York", "pais": "EEUU", "continente": "América",
            "tipo": "ciudad", "precio_desde": 950,
            "imagen_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=800&h=500&fit=crop",
            "descripcion": "La Gran Manzana nunca duerme. Broadway, Central Park, los rascacielos de Manhattan y la Estatua de la Libertad esperan en la ciudad que lo tiene todo.",
            "valoracion": 4.6, "actividades": "broadway,museos,shopping,gastronomía,arquitectura",
            "clima": "Húmedo continental", "mejor_epoca": "Abr – Jun / Sep – Nov",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
        {
            "id": 13, "nombre": "Roma", "pais": "Italia", "continente": "Europa",
            "tipo": "ciudad", "precio_desde": 550,
            "imagen_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&h=500&fit=crop",
            "descripcion": "La ciudad eterna. Roma es un museo al aire libre: el Coliseo, el Vaticano, la Fontana de Trevi... 3000 años de historia a cada vuelta de esquina.",
            "valoracion": 4.7, "actividades": "historia,gastronomía,arte,arquitectura,Vaticano",
            "clima": "Mediterráneo", "mejor_epoca": "Abr – Jun / Sep – Oct",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
        {
            "id": 14, "nombre": "Barcelona", "pais": "España", "continente": "Europa",
            "tipo": "ciudad", "precio_desde": 380,
            "imagen_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&h=500&fit=crop",
            "descripcion": "La ciudad de Gaudí. Arquitectura modernista única, playas urbanas, gastronomía mediterránea y la mejor vida nocturna de Europa.",
            "valoracion": 4.6, "actividades": "arquitectura modernista,playas,gastronomía,vida nocturna,museos",
            "clima": "Mediterráneo", "mejor_epoca": "May – Oct",
            "paquetes": [
                {"nombre": "Barcelona City Break", "precio": 350, "duracion_dias": 3, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Fin de semana con Sagrada Família y Park Güell incluidos"},
                {"nombre": "Barcelona Completo", "precio": 580, "duracion_dias": 5, "incluye_vuelo": True, "incluye_hotel": True, "num_viajeros": 2, "descripcion": "Una semana descubriendo el modernismo catalán con gastronomía"},
            ],
            "hoteles": [
                {"nombre": "W Barcelona", "categoria": 5, "precio_noche": 380, "descripcion": "Icónico hotel vela en la Barceloneta con vistas al mar", "servicios": "piscina infinity,spa,playa privada,rooftop bar"},
                {"nombre": "Hotel Arts Barcelona", "categoria": 5, "precio_noche": 350, "descripcion": "Rascacielos de lujo en el Port Olímpic", "servicios": "piscina,spa,restaurante Michelin,gym"},
                {"nombre": "Room Mate Pau", "categoria": 3, "precio_noche": 110, "descripcion": "Hotel boutique moderno en el Eixample a 5 min de Las Ramblas", "servicios": "wifi,desayuno,terraza"},
            ],
            "valoraciones": [
                {"usuario_nombre": "Luis Martínez", "puntuacion": 4.6, "comentario": "Barcelona tiene todo: sol, playa, arquitectura única y la mejor comida. 100% recomendable.", "fecha": "2025-04-20"},
            ],
        },
        {
            "id": 15, "nombre": "Ámsterdam", "pais": "Países Bajos", "continente": "Europa",
            "tipo": "ciudad", "precio_desde": 480,
            "imagen_url": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=800&h=500&fit=crop",
            "descripcion": "La Venecia del Norte. Canales históricos, el Rijksmuseum, el Museo Van Gogh y un ambiente cosmopolita y libre que enamora a todo visitante.",
            "valoracion": 4.5, "actividades": "canales,museos,ciclismo,gastronomía,mercados",
            "clima": "Oceánico", "mejor_epoca": "Abr – Oct",
            "paquetes": [], "hoteles": [], "valoraciones": [],
        },
    ]

    col.insert_many(destinos)
    col.create_index("id", unique=True)
    col.create_index("tipo")
    col.create_index("continente")
    col.create_index("valoracion")
    print("✅ MongoDB inicializado con datos de ejemplo")
