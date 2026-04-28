# Sistema RSS – Documento Detallado de Funcionamiento e Integración

Este documento recopila toda la información necesaria para entender cómo se gestionan los RSS en el proyecto y cómo el frontend debe integrarse con el backend.

---

## 1. Fuente de datos inicial

El archivo:

```
data/rss_sources.json
```

Contiene:

* Medios (ej: RTVE, El País, ABC…)
* Canales RSS por medio (100+ feeds)
* Categorías IPTC

Este archivo NO se usa directamente en frontend ni en tiempo real. Solo sirve para inicializar el sistema.

---

## 2. Inicialización de datos (seed)

Script:

```
backend/newsradar_api/app/seed.py
```

Qué hace:

1. Lee `rss_sources.json`
2. Inserta categorías IPTC (Política, Economía, etc.)
3. Inserta fuentes de información (medios)
4. Inserta canales RSS asociados a cada fuente

Ejecución:

```bash
cd backend/newsradar_api
python app/seed.py
```

Resultado:

* Base de datos relacional con:

  * categorías
  * fuentes
  * canales RSS

---

## 3. Procesamiento automático de RSS

Archivo clave:

```
rss_worker.py
```

### Problema

Cada RSS puede tener estructuras distintas.

### Solución

Se usa la librería `feedparser`, que normaliza automáticamente diferentes formatos RSS/Atom.

### Ejemplo de procesamiento

```python
feed = feedparser.parse(channel.url)

for entry in feed.entries:
    article = {
        "title": entry.get("title", ""),
        "description": entry.get("summary", "") or entry.get("description", ""),
        "url": entry.get("link", ""),
        "published_date": parse_date(entry.get("published", ""))
    }
```

### Claves importantes

* No se procesa RSS uno a uno manualmente
* `feedparser` unifica campos comunes
* Se usan fallbacks (`summary` vs `description`)
* Las fechas se normalizan con `_parse_date()`

---

## 4. Clasificación y enriquecimiento

Después de parsear:

* Se clasifica la noticia en categoría IPTC
* Se asocia a alertas de usuario

Ejemplo:

```python
{
  **article,
  "iptc_category": classify_iptc_level1(text),
  "alert_id": alert_id
}
```

---

## 5. Almacenamiento

### Base de datos relacional

Guarda:

* categorías
* fuentes
* canales RSS

### MongoDB

Guarda noticias procesadas:

```json
{
  "title": "...",
  "description": "...",
  "url": "...",
  "published_date": "...",
  "iptc_category": "...",
  "alert_id": "..."
}
```

---

## 6. Flujo completo del sistema

```
rss_sources.json
   ↓
seed.py
   ↓
BD relacional (fuentes + canales)
   ↓
RSSWorker (procesa feeds)
   ↓
feedparser (normaliza)
   ↓
MongoDB (noticias)
   ↓
API REST
   ↓
Frontend
```

---

## 7. Backend – API disponible

Base URL:

```
http://localhost:8000/api/v1
```

### Endpoints principales

* `GET /categories`
* `GET /information-sources`
* `GET /information-sources/{id}/rss-channels`
* `GET /users/{id}/alerts`
* `GET /users/{id}/alerts/{id}/notifications`
* `POST /alerts/suggest-synonyms`

---

## 8. Cómo debe trabajar el frontend

### IMPORTANTE

El frontend:

* ❌ NO consume RSS directamente
* ❌ NO parsea feeds
* ❌ NO adapta formatos

El frontend SOLO consume la API.

---

## 9. Patrón actual vs necesario

### Actual (mock)

```javascript
const response = {
  fuentes: { activas: 12, rss: 104 },
  noticias: { hoy: 145 },
  alertas: 8
};
```

### Objetivo (real)

```javascript
const response = await axios.get('/information-sources');
```

---

## 10. Servicios frontend recomendados

Archivo sugerido:

```
frontend/src/services/newsService.js
```

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const getCategories = (token) => {
  return axios.get(`${API_URL}/categories`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getInformationSources = (token) => {
  return axios.get(`${API_URL}/information-sources`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getRSSChannels = (sourceId, token) => {
  return axios.get(`${API_URL}/information-sources/${sourceId}/rss-channels`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getUserAlerts = (userId, token) => {
  return axios.get(`${API_URL}/users/${userId}/alerts`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getAlertNotifications = (userId, alertId, token) => {
  return axios.get(`${API_URL}/users/${userId}/alerts/${alertId}/notifications`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};
```

---

## 11. Integración en componentes

### Dashboard

```javascript
useEffect(() => {
  const loadData = async () => {
    const token = getToken();

    const [sources, alerts] = await Promise.all([
      getInformationSources(token),
      getUserAlerts(userId, token)
    ]);

    setData({
      fuentes: sources.data.length,
      alertas: alerts.data.length
    });
  };

  loadData();
}, []);
```

---

## 12. Autenticación

Todas las requests requieren:

```javascript
headers: {
  Authorization: `Bearer ${token}`
}
```

---

## 13. CORS

Ya configurado en backend para:

* [http://localhost:5173](http://localhost:5173)

---

## 14. Idea clave final

* Los RSS son COMPLETAMENTE responsabilidad del backend
* La normalización ocurre con `feedparser`
* MongoDB guarda datos limpios
* El frontend solo consume JSON estructurado

---

## Resumen corto

* `rss_sources.json` → define fuentes
* `seed.py` → carga estructura
* `rss_worker.py` → procesa feeds
* `feedparser` → unifica formatos
* MongoDB → guarda noticias
* API → expone datos
* Frontend → consume API

