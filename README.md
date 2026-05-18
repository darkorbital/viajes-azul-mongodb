# Viajes Azul SL — MongoDB Edition

Versión del recomendador de viajes usando **MongoDB Atlas** como base de datos en lugar de SQLite.
Mismo frontend, misma API REST, distinto modelo de datos.

## Diferencia principal: relacional vs. documental

| SQLite (versión original) | MongoDB (esta versión) |
|---|---|
| 5 tablas con claves foráneas | 1 colección con documentos embebidos |
| JOINs para obtener paquetes/hoteles | Una sola lectura por destino |
| Schema rígido | Schema flexible |
| Archivo local `.db` | Base de datos en la nube (Atlas) |

```json
// En MongoDB, un destino incluye todo dentro del mismo documento:
{
  "nombre": "Bali",
  "tipo": "playa",
  "precio_desde": 1100,
  "paquetes": [ { "nombre": "Bali Surf & Relax", "precio": 1350 } ],
  "hoteles":  [ { "nombre": "Alaya Resort Ubud", "categoria": 4 } ],
  "valoraciones": [ { "puntuacion": 5, "comentario": "..." } ]
}
```

## Configuración de MongoDB Atlas

1. Crea una cuenta gratuita en [cloud.mongodb.com](https://cloud.mongodb.com)
2. Crea un cluster (M0 Free Tier)
3. En **Database Access**: crea un usuario con contraseña
4. En **Network Access**: añade `0.0.0.0/0` (permitir cualquier IP)
5. En **Connect → Drivers**: copia la URI de conexión

## Instalación y arranque

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar la URI de MongoDB Atlas
cp .env.example .env
# Edita .env y pega tu URI:
# MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/viajes_azul

# 3. Arrancar
python3 app.py

# 4. Abrir en el navegador
#    → http://localhost:5001
```

La colección `destinos` se crea y puebla automáticamente en el primer arranque.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + Flask 3 |
| Base de datos | MongoDB Atlas (pymongo) |
| Frontend | HTML5 + Tailwind CSS + Vanilla JS |
| Despliegue | Render |

---

Proyecto de Ingeniería · Universidad Europea de Madrid · 2025
**Victor Vila Gomez**
