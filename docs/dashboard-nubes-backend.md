# Backend: Dashboard y Nubes (Datos compilados + IA)

Este documento describe cómo el backend compila los datos que necesita el frontend para:

1. `frontend/src/pages/dashboard/dashboard.jsx` (Dashboard)
2. `frontend/src/pages/resumen/nubes.jsx` (Nubes de palabras)

El objetivo es que el frontend **solo consuma endpoints** con el shape ya listo para pintar.

## Resumen de endpoints

Base path:

- `/api/v1`

### Dashboard

- `GET /api/v1/dashboard?days=7`

Devuelve KPIs + series para gráfica de evolución + distribución por categorías.

### Nubes

- `GET /api/v1/resumen/clouds/global?days=30&limit=20`
- `GET /api/v1/resumen/clouds/{category}?days=30&limit=20`

Devuelve una lista de `{term, count}` lista para pintar.

`category` esperada por el frontend (ver `nubes.jsx`):

- `culture`, `consumption`, `sports`, `economy`, `entertainment`,
  `government`, `international`, `national`, `politics`, `technology`

## Autenticación

Estos endpoints requieren `Authorization: Bearer <token>`.

Token de ejemplo:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@newsradar.com","password":"admin123"}'
```

## Dashboard: shape de respuesta

Endpoint:

- `GET /api/v1/dashboard?days=7`

Respuesta (shape):

```json
{
  "fuentes": { "activas": 12, "rss": 104 },
  "noticias": { "hoy": 145, "semana": 1420 },
  "alertas": 8,
  "evolucion": [
    { "name": "Mon", "date": "2026-04-30", "noticias": 45 }
  ],
  "categorias": [
    { "key": "politics", "name": "Politics", "value": 400 }
  ]
}
```

Notas:

- `days` controla el periodo para `evolucion` y para el conteo de `noticias.semana` (aunque el campo se llame "semana").
- `evolucion[].name` es una etiqueta corta (Mon/Lun), se genera usando `Accept-Language` si viene en headers.

### Fuente de datos

- Postgres:
  - `information_sources` -> `fuentes.activas`
  - `rss_channels` -> `fuentes.rss`
  - `alerts` -> `alertas`
- MongoDB:
  - `news`:
    - conteo de hoy: por `created_at >= start_of_day_utc`
    - conteo periodo: por `created_at >= now - days`
    - `evolucion`: agregación por día en `created_at`
    - `categorias`: buckets por `iptc_category`

Implementación:

- `backend/newsradar_api/app/services/analytics_service.py:build_dashboard`
- `backend/newsradar_api/app/main.py:GET /api/v1/dashboard`

## Nubes: shape de respuesta

Endpoints:

- `GET /api/v1/resumen/clouds/global?days=30&limit=20`
- `GET /api/v1/resumen/clouds/{category}?days=30&limit=20`

Respuesta (shape):

```json
[
  { "term": "INTELIGENCIA ARTIFICIAL", "count": 98 },
  { "term": "CIBERSEGURIDAD", "count": 55 }
]
```

### Cómo se calculan

El backend:

1. Obtiene las alertas del usuario autenticado desde Postgres.
2. Toma solo las noticias recientes de Mongo (`news`) asociadas a esas alertas del usuario.
3. (Si es por categoría) filtra por categoría usando un mapeo desde `iptc_category` a las 10 categorías del frontend.
4. Pasa un subconjunto (hasta 200 noticias) a la IA para extraer `{term,count}`.
5. Devuelve lista ya lista para UI.

Consecuencia funcional:

- La nube global no representa "todas las noticias del sistema".
- La nube global representa solo noticias pertenecientes a alertas del usuario autenticado.
- Si el usuario no tiene alertas, la respuesta es `[]`.

Implementación:

- `backend/newsradar_api/app/services/analytics_service.py:build_wordcloud`
- `backend/newsradar_api/app/services/ia_service.py:generate_wordcloud_terms`
- `backend/newsradar_api/app/main.py:GET /api/v1/resumen/clouds/...`

### Uso de IA

La IA se usa para convertir texto de noticias (título + descripción) en una nube de términos.

Variables de entorno recomendadas (Gemini / Google AI Studio):

```bash
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-flash
```

## Cache (para evitar llamadas a IA en cada refresh)

Colección en Mongo:

- `wordcloud_cache`

El cache se indexa por:

- scope (`global` o `category`)
- category (si aplica)
- user_id
- days
- limit
- lang (derivado de `Accept-Language`)

Política actual:

- `cache_max_age_hours = 6`
- si el cache está fresco, se devuelve directamente
- si está viejo/no existe, se recalcula y se actualiza

## Mapeo de categorías (IPTC -> Nubes)

Las noticias guardan `iptc_category` (ej: `Politics`, `Business`, `Technology`, ...).

Para encajar con las 10 categorías del frontend, se aplica un mapeo pragmático:

- `Politics` -> `politics`
- `Business` -> `economy`
- `Sports` -> `sports`
- `Entertainment` -> `entertainment`
- `Technology` / `Science` -> `technology`
- `Health` -> `consumption`
- `Lifestyle` -> `culture`
- `World` -> `international`
- `General` / otros -> `national`

Si queréis un mapeo distinto (o queréis basarlo en vuestra tabla `categories` / `category_id` en vez de IPTC),
ajustad el mapping en:

- `backend/newsradar_api/app/services/analytics_service.py`

## Cómo probar (curl)

1) Login:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@newsradar.com","password":"admin123"}'
```

2) Dashboard:

```bash
curl -s http://localhost:8000/api/v1/dashboard?days=7 \
  -H "Authorization: Bearer TU_TOKEN"
```

3) Nube global:

```bash
curl -s "http://localhost:8000/api/v1/resumen/clouds/global?days=30&limit=20" \
  -H "Authorization: Bearer TU_TOKEN"
```

4) Nube por categoria:

```bash
curl -s "http://localhost:8000/api/v1/resumen/clouds/technology?days=30&limit=20" \
  -H "Authorization: Bearer TU_TOKEN"
```

## Integración en frontend (guía rápida)

El frontend ya tiene mocks en:

- `frontend/src/pages/dashboard/dashboard.jsx`
- `frontend/src/pages/resumen/nubes.jsx`

La integración consiste en **reemplazar los mocks por llamadas HTTP** a los endpoints del backend.

### Requisitos

- Tener el `token` (Bearer) disponible donde el frontend lo gestione (localStorage/context/etc).
- Usar la base URL que ya tengáis configurada (p. ej. `VITE_API_URL`).

Ejemplo (helper mínimo):

```js
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const token = localStorage.getItem('token'); // o donde lo guardeis

const apiFetch = async (path) => {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Accept-Language': navigator.language || 'en',
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};
```

### Dashboard (`dashboard.jsx`)

Reemplazar `fetchDashboardData()` para que haga:

```js
const response = await apiFetch(`/api/v1/dashboard?days=7`);
setData(response);
```

Si queréis que el toggle 1D/7D afecte al backend, entonces:

```js
const days = newsFilter === '1D' ? 1 : 7;
const response = await apiFetch(`/api/v1/dashboard?days=${days}`);
setData(response);
```

### Nubes (`nubes.jsx`)

Reemplazar:

- `fetchNubeGlobal()` por:

```js
return apiFetch(`/api/v1/resumen/clouds/global?days=30&limit=20`);
```

- `fetchNubeCategoria(categoria)` por:

```js
return apiFetch(`/api/v1/resumen/clouds/${categoria}?days=30&limit=20`);
```

Con eso, `WordCloud` ya puede pintar directamente porque la respuesta es `[{term, count}]`.
