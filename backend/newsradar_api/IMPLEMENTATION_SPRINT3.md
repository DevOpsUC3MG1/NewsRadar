# Sprint 3: Implementación RSS, IA y Worker

Documento de implementación para el Sprint 3 con todas las tareas completadas.

---

## 📋 Tareas Completadas

### 1. ✅ CRUD Alertas
**Estado**: YA EXISTÍA
- `GET /api/v1/users/{user_id}/alerts` - Listar alertas
- `POST /api/v1/users/{user_id}/alerts` - Crear alerta
- `GET /api/v1/users/{user_id}/alerts/{alert_id}` - Obtener alerta
- `PUT /api/v1/users/{user_id}/alerts/{alert_id}` - Actualizar alerta
- `DELETE /api/v1/users/{user_id}/alerts/{alert_id}` - Eliminar alerta

**Requisito relacionado**: RF-02 (Alertas configurables)

---

### 2. ✅ Integración IA: Generación de Sinónimos

**Ubicación**: `app/services/ia_service.py`  
**Proveedor**: OpenAI API (gpt-3.5-turbo)

**Nuevo endpoint**:
```
POST /api/v1/alerts/suggest-synonyms
Content-Type: application/json

{
  "keywords": ["inteligencia artificial", "machine learning"],
  "max_synonyms": 5
}

Response (200):
{
  "keywords": ["inteligencia artificial", "machine learning"],
  "suggested_synonyms": [
    "deep learning",
    "redes neuronales",
    "algoritmos de aprendizaje",
    "IA generativa",
    "modelos predictivos"
  ]
}
```

**Flujo RF-02** (Sugerencia automática de sinónimos):
1. Frontend llama a `/suggest-synonyms` mientras el usuario escribe palabras clave
2. Backend devuelve sugerencias con OpenAI
3. Usuario acepta o rechaza las sugerencias
4. Al crear la alerta, guarda los descriptores finales

**Documentación**: Ver `PROMPTS.md` para detalles de prompt (RNF-06)

---

### 3. ✅ Clasificación Automática IPTC

**Ubicación**: `app/services/ia_service.py:classify_iptc_level1()`  
**Proveedor**: OpenAI API (gpt-3.5-turbo)  
**Ejecución**: Automática en background

**Categorías IPTC Nivel 1**:
- Politics
- Business
- Sports
- Entertainment
- Science
- Technology
- Health
- Lifestyle
- World
- General

**RF-05** (Clasificación de información):
- Se ejecuta automáticamente para cada noticia del RSS
- Clasifica en 1 categoría IPTC de nivel 1
- Se guarda en MongoDB junto a los datos de la noticia

**Documentación**: Ver `PROMPTS.md` para detalles de prompt (RNF-06)

---

### 4. ✅ Worker RSS: Proceso de Ingesta y MongoDB

**Ubicación**: `app/services/rss_worker.py`  
**Clase principal**: `RSSWorker`

**Flujo completo**:
1. **Trigger**: APScheduler ejecuta según `cron_expression` de cada alerta
2. **Fetch**: Descarga canales RSS (feedparser)
3. **Detección**: Busca artículos que contengan descriptores/sinónimos
4. **Clasificación**: Asigna categoría IPTC automáticamente
5. **Almacenamiento**: Guarda en MongoDB colección `news`
6. **Estadísticas**: Retorna stats para notificaciones

**RF-03** (Expresiones cron por alerta):
- Cada alerta tiene un `cron_expression`
- El worker respeta la frecuencia individual de cada alerta

**Documento guardado en MongoDB**:
```javascript
{
  "_id": ObjectId(...),
  "title": "La IA revoluciona el sector bancario",
  "description": "Los bancos implementan soluciones de IA...",
  "url": "https://noticia.com/articulo",
  "channel_id": 1,
  "source_origin": "1",  // information_source_id
  "published_date": ISODate("2024-04-20T10:00:00Z"),
  "iptc_category": "Technology",
  "alert_id": 5,
  "created_at": ISODate("2024-04-20T11:20:00Z")
}
```

---

## 🚀 Cómo Usar

### 1. Instalar Dependencias
```bash
cd backend/newsradar_api
pip install -r requirements.txt
```

**Nuevas dependencias agregadas**:
- `openai==1.3.0` - Cliente de OpenAI
- `feedparser==6.0.10` - Parser de RSS/Atom feeds
- `apscheduler==3.10.4` - Scheduler de tareas en background

### 2. Configurar Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# OpenAI (requerido para sinónimos e IPTC)
OPENAI_API_KEY=sk-...          # Obtén en https://platform.openai.com/account/api-keys
OPENAI_MODEL=gpt-3.5-turbo

# Email (ya configurado, opcional si quieres verificación)
GMAIL_SENDER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop

# Bases de datos
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/newsradar_core
MONGODB_URL=mongodb://localhost:27017
```

### 3. Iniciar Backend

```bash
source /path/to/venv/bin/activate
cd backend/newsradar_api
uvicorn app.main:app --reload
```

El scheduler se inicializa automáticamente:
- **Startup**: Lee todas las alertas y programa los jobs
- **Shutdown**: Detiene todos los jobs activos

---

## 🔧 Arquitectura

```
app/
├── main.py                      # FastAPI + Endpoints + Scheduler
├── models.py                    # ORM (SQLAlchemy)
├── database.py                  # PostgreSQL connection
├── database_mongodb.py          # MongoDB connection
└── services/
    ├── __init__.py
    ├── ia_service.py            # OpenAI API calls (sinónimos + IPTC)
    └── rss_worker.py            # RSS fetching, parsing, classification, storage
```

---

## 📊 API Endpoints Nueva/Modificada

### Endpoint Nuevo
```
POST /api/v1/alerts/suggest-synonyms
  - Genera sinónimos para palabras clave
  - Headers: Authorization: Bearer {token}
  - Body: {"keywords": [...], "max_synonyms": 5}
```

### Endpoints Existentes (Sin Cambios)
```
GET    /api/v1/users/{user_id}/alerts
POST   /api/v1/users/{user_id}/alerts
GET    /api/v1/users/{user_id}/alerts/{alert_id}
PUT    /api/v1/users/{user_id}/alerts/{alert_id}
DELETE /api/v1/users/{user_id}/alerts/{alert_id}
```

---

## 📝 Trazabilidad de Prompts (RNF-06)

Todos los prompts de IA están documentados en `PROMPTS.md`:

| Prompt ID | Nombre | Modelo | Propósito |
|-----------|--------|--------|-----------|
| IA-001 | Generación de sinónimos | gpt-3.5-turbo | Ampliar cobertura de búsqueda |
| IA-002 | Clasificación IPTC | gpt-3.5-turbo | Asignar categorías automáticas |

---

## 🧪 Testing y Debugging

### Ver logs del scheduler
```bash
# En uvicorn, verás:
INFO: Iniciando procesamiento de alerta 5
INFO: Alerta 5 procesada. Stats: {'articles_detected': 3, 'articles_stored': 2, ...}
```

### Probar endpoint de sí­nimos
```bash
curl -X POST http://localhost:8000/api/v1/alerts/suggest-synonyms \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["covid", "pandemia"], "max_synonyms": 5}'
```

### Monitorear MongoDB
```bash
mongosh
> use newsradar_archive
> db.news.find().pretty()
> db.news.countDocuments()
```

---

## ⚠️ Consideraciones de Producción

1. **OpenAI Costs**: Cada llamada a API cuesta dinero. Monitorear usage en dashboard.
2. **Rate Limits**: OpenAI tiene límites. Implementar retry logic (ya está en try/except).
3. **Redis para Tokens**: Los reset tokens están en memoria. En producción, usar Redis con TTL.
4. **Celery para Workers**: Para escalar, migrar de APScheduler a Celery + Redis.
5. **Monitoring**: Agregar APM (Sentry, New Relic) para trazar errores.

---

## 📚 Referencias

- **Requisitos RF-02, RF-03, RF-05**: Implementados ✅
- **Requisito RNF-06**: Prompts documentados en `PROMPTS.md` ✅
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **APScheduler**: https://apscheduler.readthedocs.io/
- **Feedparser**: https://feedparser.readthedocs.io/

---

## ✅ Checklist Final

- [x] Sincronización automática de jobs al startup
- [x] Detección de palabras clave en artículos RSS
- [x] Clasificación IPTC automática
- [x] Almacenamiento en MongoDB con todos los campos
- [x] Endpoint /suggest-synonyms funcional
- [x] Documentación de prompts (RNF-06)
- [x] Error handling y logging
- [x] Variables de entorno configurables
- [x] Compilación sin errores de sintaxis

**Próximos pasos**: Implementar notificaciones vía email/SMS con estadísticas del worker.
