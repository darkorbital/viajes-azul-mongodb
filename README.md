# ✈️ Viajes Azul SL — Recomendador Inteligente de Viajes · MongoDB Edition

<p align="center">
  <img src="https://img.shields.io/badge/Sprint-1%20MVP-2563eb?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.11-3776ab?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-Atlas-00ed64?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Render-Live-46e3b7?style=for-the-badge&logo=render&logoColor=white" />
</p>

<p align="center">
  <b>MVP de un recomendador de viajes con chatbot IA y base de datos documental en la nube</b><br/>
  Caso práctico de Transformación Digital · Universidad Europea de Madrid
</p>

---

## 🎯 ¿De dónde surge este proyecto?

Este proyecto nace como **caso práctico de Transformación Digital** en la Universidad Europea de Madrid. La empresa ficticia **Viajes Azul SL** había detectado una oportunidad de mercado: sus clientes no querían un catálogo de viajes más, sino un sistema que les *ayudase a decidir*.

Tras sesiones de **Design Thinking**, los insights fueron claros:

| Lo que el usuario quiere | Lo que el sistema debe hacer |
|---|---|
| Simplicidad al elegir destino | Filtros intuitivos y búsqueda instantánea |
| Soporte en la decisión | Chatbot que recomienda según perfil |
| Maximizar coste/beneficio | Comparativa de paquetes y precios |
| Compartir la experiencia | Sistema de valoraciones reales |

La solución: un **recomendador web inteligente** con chatbot conversacional, construido siguiendo metodología Scrum en un Sprint de 2 semanas, usando **MongoDB Atlas** como base de datos documental en la nube.

---

## 🚀 ¿Qué hace la aplicación?

### Buscador y filtros en tiempo real
El usuario puede buscar por nombre, país o tipo de actividad. Los filtros por tipo de destino (playa / montaña / ciudad), presupuesto y continente se aplican instantáneamente sin recargar la página. En MongoDB, cada cambio en los filtros genera un diccionario de filtro que pymongo traduce a una consulta optimizada.

### Catálogo de 15 destinos curados
Cada destino es un **documento MongoDB** que contiene su descripción, valoración media, precio desde, clima, mejor época, y arrays embebidos de paquetes, hoteles y valoraciones. Las tarjetas muestran un badge dinámico y la etiqueta **⭐ Top rated** para los destinos mejor valorados.

### Modal de detalle completo
Al hacer clic en cualquier destino se despliega un panel con tres pestañas:
- **Paquetes** — opciones con vuelo + hotel, precio por persona y duración
- **Hoteles** — alojamientos de 3 a 5 estrellas con servicios y precio por noche
- **Valoraciones** — reseñas de viajeros con puntuación y formulario para dejar la tuya

Con MongoDB, las tres pestañas se sirven desde **una sola lectura** a la base de datos: no hay JOINs, todo está embebido en el mismo documento.

### 🤖 Chatbot "Azul" — la funcionalidad avanzada
El asistente conversacional entiende consultas en español natural y consulta MongoDB en tiempo real:

```
Usuario → "quiero aventura y montaña"

Azul    → 🤿 ¡Para los amantes de la aventura!
            • Patagonia, Argentina / Chile — desde 1600€
            • Bali, Indonesia — desde 1100€
            • Zermatt, Suiza — desde 1800€
          ¿Cuál se ajusta mejor a tu nivel de aventura?
```

Internamente, el chatbot extrae keywords del mensaje y construye un filtro MongoDB:

```python
{"actividades": {"$regex": "trekking|surf|alpinismo", "$options": "i"}}
```

### Sistema de valoraciones
Los usuarios pueden dejar reseñas con puntuación de 1 a 5 estrellas. La operación usa `$push` para añadir la valoración al array embebido y `$set` para actualizar la media — todo en una sola operación atómica, sin transacciones complejas.

---

## 🏗️ Arquitectura técnica

```
┌─────────────────────────────────────────────────────────────┐
│                      NAVEGADOR (Cliente)                     │
│  HTML + Tailwind CSS + Vanilla JS                           │
│  fetch() → API REST → renderizado dinámico sin recarga      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / JSON
┌────────────────────────▼────────────────────────────────────┐
│                   BACKEND (Flask · Python)                   │
│                                                             │
│  GET  /api/destinos        → filtro pymongo dinámico        │
│  GET  /api/destinos/<id>   → documento completo (1 lectura) │
│  POST /api/chatbot         → motor de intenciones           │
│  POST /api/valoraciones    → $push + $set atómico           │
│  GET  /api/stats           → count_documents + aggregate    │
└────────────────────────┬────────────────────────────────────┘
                         │ pymongo + TLS (certifi)
┌────────────────────────▼────────────────────────────────────┐
│               BASE DE DATOS (MongoDB Atlas)                  │
│                                                             │
│  Colección: destinos                                        │
│  ├── paquetes    [array embebido]                           │
│  ├── hoteles     [array embebido]                           │
│  └── valoraciones [array embebido]                          │
│                                                             │
│  Índices: id (unique), tipo, continente, valoracion         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Modelo de datos

A diferencia del modelo relacional con 5 tablas, aquí cada destino es un **documento** que contiene toda su información relacionada como arrays embebidos:

```json
{
  "id": 2,
  "nombre": "Bali",
  "pais": "Indonesia",
  "continente": "Asia",
  "tipo": "playa",
  "precio_desde": 1100,
  "valoracion": 4.8,
  "actividades": "surf,yoga,templos,spa,buceo,senderismo",
  "clima": "Tropical",
  "mejor_epoca": "Mayo – Septiembre",

  "paquetes": [
    {
      "nombre": "Bali Surf & Relax",
      "precio": 1350,
      "duracion_dias": 8,
      "incluye_vuelo": true,
      "incluye_hotel": true,
      "num_viajeros": 2
    }
  ],

  "hoteles": [
    {
      "nombre": "Alaya Resort Ubud",
      "categoria": 4,
      "precio_noche": 180,
      "servicios": "piscina,spa,clases cocina balinesa"
    }
  ],

  "valoraciones": [
    {
      "usuario_nombre": "María Fernández",
      "puntuacion": 5.0,
      "comentario": "Bali superó todas mis expectativas.",
      "fecha": "2025-04-01"
    }
  ]
}
```

**¿Por qué documentos embebidos?**
Los paquetes, hoteles y valoraciones de un destino siempre se acceden juntos. Embeberlos elimina los JOINs, reduce la latencia y simplifica el código.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Por qué |
|---|---|---|
| Backend | Python 3.11 + Flask 3 | Ligero, ideal para MVPs y APIs REST |
| Base de datos | MongoDB Atlas (Free Tier) | NoSQL documental, sin servidor, escala global |
| Driver BD | pymongo + certifi | Cliente oficial MongoDB para Python con TLS |
| Frontend | HTML5 + Tailwind CSS | Diseño profesional sin build process |
| JS | Vanilla JS (ES2022) | Sin frameworks innecesarios para un MVP |
| Servidor producción | Gunicorn | WSGI estándar para Flask en producción |
| Despliegue | Render | Cloud gratuito, despliegue desde GitHub |

---

## ⚙️ Configuración de MongoDB Atlas

1. Crea una cuenta gratuita en [cloud.mongodb.com](https://cloud.mongodb.com)
2. Crea un cluster **M0 Free Tier** (elige la región más cercana)
3. En **Database Access**: crea un usuario con contraseña
4. En **Network Access**: añade `0.0.0.0/0` para permitir conexiones desde cualquier IP
5. En **Connect → Drivers → Python**: copia tu URI de conexión
6. Crea el fichero `.env` en la raíz del proyecto:

```env
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/viajes_azul?appName=azul
```

---

## ▶️ Cómo ejecutarlo en local

```bash
# 1. Clonar el repositorio
git clone https://github.com/darkorbital/viajes-azul-mongodb.git
cd viajes-azul-mongodb

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar MongoDB Atlas
cp .env.example .env
# Edita .env y pega tu URI de conexión

# 4. Arrancar el servidor de desarrollo
python3 app.py

# 5. Abrir en el navegador
#    → http://localhost:5001
```

La colección `destinos` se crea y puebla automáticamente en el primer arranque con 15 destinos, 13 paquetes, 13 hoteles y 10 valoraciones de ejemplo.

---

## 💡 Valor del proyecto

Este MVP demuestra la diferencia práctica entre un modelo **relacional** y uno **documental**:

- **Para el desarrollador:** el código de consulta es más simple — un diccionario Python en vez de SQL con JOINs. El detalle de un destino pasa de 4 consultas a 1 sola lectura.
- **Para el negocio:** MongoDB Atlas escala horizontalmente sin cambiar el código. Pasar de 15 a 15.000 destinos no requiere ninguna migración.
- **Para escalar:** la arquitectura está lista para sustituir el chatbot por un LLM real (GPT-4), añadir índices de texto completo nativos de MongoDB, y desplegarse en cualquier región del mundo.

---

## 🗺️ Roadmap

- **Sprint 2** — Integración con LLM real · Perfil de usuario con preferencias persistidas en MongoDB · Recomendación colaborativa
- **Sprint 3** — Zona social · Programa de fidelización · Chat grupal entre viajeros
- **Sprint 4** — App móvil (React Native) · Análisis de fotos con IA · Guía interactiva AR

---

## 📁 Estructura del proyecto

```
viajes-azul-mongodb/
├── app.py                    # Flask: rutas API + motor chatbot (pymongo)
├── database.py               # Modelo de documentos MongoDB + seed data
├── requirements.txt          # Flask + Gunicorn + pymongo + certifi
├── .env.example              # Plantilla de configuración
├── .env                      # URI de MongoDB Atlas (no se sube a git)
├── templates/
│   └── index.html            # SPA: hero, filtros, cards, modal, chatbot
└── static/
    ├── css/style.css         # Estilos custom (tema azul corporativo)
    └── js/app.js             # Lógica frontend: fetch, render, chatbot UI
```

---

<p align="center">
  Proyecto de Ingeniería · Universidad Europea de Madrid · 2025<br/>
  <b>Victor Vila Gomez</b>
</p>
