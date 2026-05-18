from flask import Flask, render_template, request, jsonify
from datetime import datetime
from database import get_db, init_db

app = Flask(__name__)
init_db()


def _serialize(doc):
    """Convierte un documento MongoDB a dict JSON-serializable."""
    if doc is None:
        return None
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


# ── Página principal ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── API: listado de destinos (con filtros) ──────────────────────────────────
# Diferencia vs SQLite: en lugar de construir una query SQL con string
# concatenation, MongoDB usa un diccionario Python como filtro.
@app.route("/api/destinos")
def api_destinos():
    tipo        = request.args.get("tipo", "")
    presupuesto = request.args.get("presupuesto", "")
    busqueda    = request.args.get("busqueda", "")
    continente  = request.args.get("continente", "")

    filtro = {}

    if tipo:
        filtro["tipo"] = tipo

    if presupuesto == "bajo":
        filtro["precio_desde"] = {"$lte": 500}
    elif presupuesto == "medio":
        filtro["precio_desde"] = {"$gt": 500, "$lte": 1500}
    elif presupuesto == "alto":
        filtro["precio_desde"] = {"$gt": 1500}

    if busqueda:
        regex = {"$regex": busqueda, "$options": "i"}
        filtro["$or"] = [
            {"nombre":      regex},
            {"pais":        regex},
            {"descripcion": regex},
            {"actividades": regex},
        ]

    if continente:
        filtro["continente"] = continente

    db = get_db()
    # Excluimos arrays embebidos del listado para no enviar datos innecesarios
    proyeccion = {"paquetes": 0, "hoteles": 0, "valoraciones": 0}
    docs = list(db.destinos.find(filtro, proyeccion).sort("valoracion", -1))
    return jsonify([_serialize(d) for d in docs])


# ── API: detalle de un destino ──────────────────────────────────────────────
# Diferencia vs SQLite: no hay JOINs. Paquetes, hoteles y valoraciones
# ya están embebidos en el mismo documento — una sola lectura a la BD.
@app.route("/api/destinos/<int:id>")
def api_destino(id):
    db = get_db()
    doc = db.destinos.find_one({"id": id})
    if not doc:
        return jsonify({"error": "Destino no encontrado"}), 404

    doc = _serialize(doc)
    return jsonify({
        "destino":      {k: v for k, v in doc.items() if k not in ("paquetes", "hoteles", "valoraciones")},
        "paquetes":     doc.get("paquetes", []),
        "hoteles":      sorted(doc.get("hoteles", []), key=lambda h: h["categoria"], reverse=True),
        "valoraciones": sorted(doc.get("valoraciones", []), key=lambda v: v["fecha"], reverse=True),
    })


# ── API: añadir valoración ──────────────────────────────────────────────────
# Diferencia vs SQLite: usamos $push para añadir al array embebido
# y $set para actualizar la media — todo en una sola operación atómica.
@app.route("/api/valoraciones", methods=["POST"])
def api_valoracion():
    data       = request.json or {}
    destino_id = data.get("destino_id")
    puntuacion = data.get("puntuacion")
    comentario = data.get("comentario", "").strip()

    if not destino_id or not puntuacion or not comentario:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nueva = {
        "usuario_nombre": "Viajero Anónimo",
        "puntuacion":     float(puntuacion),
        "comentario":     comentario,
        "fecha":          datetime.now().strftime("%Y-%m-%d"),
    }

    db = get_db()
    db.destinos.update_one({"id": destino_id}, {"$push": {"valoraciones": nueva}})

    doc = db.destinos.find_one({"id": destino_id}, {"valoraciones": 1})
    valoraciones = doc.get("valoraciones", [])
    nueva_media  = round(sum(v["puntuacion"] for v in valoraciones) / len(valoraciones), 1)

    db.destinos.update_one({"id": destino_id}, {"$set": {"valoracion": nueva_media}})
    return jsonify({"ok": True, "nueva_media": nueva_media})


# ── API: estadísticas para el dashboard ────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    db = get_db()
    n_destinos    = db.destinos.count_documents({})
    pipeline_paq  = [{"$project": {"n": {"$size": "$paquetes"}}}, {"$group": {"_id": None, "total": {"$sum": "$n"}}}]
    n_paquetes    = next(iter(db.destinos.aggregate(pipeline_paq)), {}).get("total", 0)
    pipeline_val  = [{"$project": {"n": {"$size": "$valoraciones"}}}, {"$group": {"_id": None, "total": {"$sum": "$n"}}}]
    n_valoraciones = next(iter(db.destinos.aggregate(pipeline_val)), {}).get("total", 0)

    top3 = list(db.destinos.find({}, {"nombre": 1, "valoracion": 1}).sort("valoracion", -1).limit(3))
    return jsonify({
        "destinos":     n_destinos,
        "paquetes":     n_paquetes,
        "valoraciones": n_valoraciones,
        "top3":         [{"nombre": d["nombre"], "valoracion": d["valoracion"]} for d in top3],
    })


# ── API: chatbot ────────────────────────────────────────────────────────────
@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    msg = (request.json or {}).get("mensaje", "").lower().strip()
    respuesta = _chatbot(msg)
    return jsonify({"respuesta": respuesta})


def _destinos_lista(filtro, limit=3):
    db   = get_db()
    docs = list(db.destinos.find(filtro, {"nombre": 1, "pais": 1, "precio_desde": 1})
                           .sort("valoracion", -1).limit(limit))
    return "\n".join(f"  • {d['nombre']}, {d['pais']} — desde {int(d['precio_desde'])}€" for d in docs)


def _chatbot(msg):
    saludos  = ["hola", "buenas", "buenos", "hey", "hi", "qué tal"]
    playas   = ["playa", "mar", "arena", "caribe", "tropical", "mediterráneo", "bucear", "snorkel"]
    montañas = ["montaña", "nieve", "esquiar", "trekking", "senderismo", "alpes", "naturaleza", "glaciar"]
    ciudades = ["ciudad", "cultura", "museo", "arte", "historia", "monumento", "urbano"]
    baratos  = ["barato", "económico", "low cost", "oferta", "presupuesto bajo", "precio"]
    aventura = ["aventura", "extremo", "adrenalina", "activo", "emoción"]
    familia  = ["familia", "niños", "hijos", "familiar", "kids"]
    pareja   = ["romántico", "pareja", "luna de miel", "honeymoon", "amor", "escapada"]
    ayuda    = ["ayuda", "qué puedes", "cómo funciona", "opciones", "help"]

    if any(k in msg for k in saludos):
        return ("¡Hola! Soy Azul, tu asistente de viajes 🌍\n"
                "Puedo ayudarte a encontrar el destino perfecto. "
                "¿Qué tipo de viaje buscas? Cuéntame si prefieres playa, montaña o ciudad, "
                "o si tienes algún presupuesto en mente.")

    if any(k in msg for k in ayuda):
        return ("Puedo ayudarte con:\n"
                "  🏖️ Recomendar destinos de playa, montaña o ciudad\n"
                "  💰 Filtrar por presupuesto (bajo, medio, alto)\n"
                "  👨‍👩‍👧 Sugerir destinos para familias o parejas\n"
                "  🤿 Encontrar destinos de aventura\n"
                "  ℹ️ Informarte sobre precios y actividades\n\n¿Por dónde empezamos?")

    if any(k in msg for k in baratos):
        lista = _destinos_lista({"precio_desde": {"$lte": 600}})
        return f"💰 Estos son nuestros destinos más económicos (menos de 600€):\n\n{lista}\n\nTodos incluyen vuelo + hotel. ¿Te interesa alguno?"

    if any(k in msg for k in familia):
        lista = _destinos_lista({"tipo": {"$in": ["playa", "ciudad"]}})
        return f"👨‍👩‍👧‍👦 Perfectos para viajar en familia:\n\n{lista}\n\nTodos cuentan con paquetes adaptados para niños. ¿Quieres más detalles?"

    if any(k in msg for k in pareja):
        lista = _destinos_lista({"valoracion": {"$gte": 4.7}, "precio_desde": {"$gt": 600}})
        return f"💑 Para una escapada romántica te recomiendo:\n\n{lista}\n\nContamos con paquetes especiales de pareja. ¿Te apetece saber más de alguno?"

    if any(k in msg for k in aventura):
        lista = _destinos_lista({"actividades": {"$regex": "trekking|surf|alpinismo", "$options": "i"}})
        return f"🤿 ¡Para los amantes de la aventura!\n\n{lista}\n\n¿Cuál se ajusta mejor a tu nivel de aventura?"

    if any(k in msg for k in playas):
        lista = _destinos_lista({"tipo": "playa"})
        return f"🏖️ Aquí tienes nuestros mejores destinos de playa:\n\n{lista}\n\n¿Quieres que te cuente más sobre alguno?"

    if any(k in msg for k in montañas):
        lista = _destinos_lista({"tipo": "montaña"})
        return f"🏔️ Destinos de montaña que te van a encantar:\n\n{lista}\n\n¿Buscas algo más específico, como esquí o senderismo?"

    if any(k in msg for k in ciudades):
        lista = _destinos_lista({"tipo": "ciudad"})
        return f"🏛️ Las ciudades más fascinantes de nuestro catálogo:\n\n{lista}\n\n¿Te interesa el turismo cultural, la gastronomía o la vida nocturna?"

    db   = get_db()
    todos = list(db.destinos.find({}, {"id": 1, "nombre": 1, "pais": 1, "precio_desde": 1, "descripcion": 1, "actividades": 1}))
    for d in todos:
        if d["nombre"].lower() in msg or d["pais"].lower() in msg:
            acts = d.get("actividades", "").replace(",", ", ") or "variadas"
            return (f"🌍 **{d['nombre']}, {d['pais']}**\n\n{d['descripcion']}\n\n"
                    f"✈️ Desde {int(d['precio_desde'])}€ por persona\n"
                    f"🎯 Actividades: {acts}\n\n"
                    "¿Te gustaría ver los paquetes disponibles o los hoteles recomendados?")

    top = _destinos_lista({})
    return (f"Mmm, no estoy seguro de entenderte 🤔 "
            f"Puedes preguntarme por tipo de destino (playa, montaña, ciudad), "
            f"presupuesto, o para quién es el viaje (familia, pareja, aventureros).\n\n"
            f"Mientras tanto, estos son nuestros destinos más valorados:\n\n{top}")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
