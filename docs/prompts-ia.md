# Registro de Prompts de IA — NewsRadar

## Metadatos del proyecto

| Campo | Valor |
|---|---|
| Proyecto | NewsRadar — Sistema de monitorización de noticias RSS |
| Equipo | 7 roles: Backend Lead, Backend Dev, Frontend Lead, Frontend Dev, QA, Scrum Master, DevOps |
| Modelo de IA | opencode/big-pickle (asistente de código conversacional) |
| Modalidad | Chat interactivo con herramientas de edición, búsqueda y ejecución |
| Período | Mayo 2026 |

---

## Plantilla de registro

Cada entrada sigue esta estructura:

```
### Prompt
[Instrucción o pregunta enviada al asistente]

### Propósito
[Objetivo de negocio/técnico que se perseguía]

### Archivos generados/modificados
- `ruta/al/archivo` — descripción del cambio

### Resultado
[Resumen del output: código generado, decisión tomada, problema diagnosticado]
```

---

## 1. Backend Lead

Rol: decisiones arquitectónicas, revisión de código, diseño de servicios, coordinación técnica.

### 1.1 Diseño del servicio de wordcloud con caché MongoDB

```
Necesito un servicio de wordcloud en el backend que:
- Lea notificaciones de MongoDB
- Genere nubes de palabras por frecuencia de términos
- Cachee resultados en MongoDB con TTL de 6h
- Tenga fallback a colección `news` si `notifications` está vacía
- Soporte filtrado por categoría (global o por categoría IPTC)
```

**Propósito:** RF-07 / Nubes de palabras — diseño del core de analytics.

**Archivos:**
- `backend/newsradar_api/app/services/analytics_service.py` — creación completa del servicio
- `backend/newsradar_api/app/main.py` — endpoints `/resumen/clouds/{category}`

**Resultado:** Implementación completa de `build_wordcloud()` con dos modos (global y por categoría), caché en MongoDB con upsert, y fallback a `news` collection.

---

### 1.2 Mapa de categorías RSS → IPTC y viceversa

```
Necesito un mapeo bidireccional entre:
- Nombres de canal RSS (ej: "Economia", "Cultura", "Deportes")
- Nombres IPTC nivel 1 (ej: "Economía, negocios y finanzas", "Artes, cultura, entretenimiento y medios")
- IDs numéricos IPTC (ej: 4000000, 1000000)

¿Dónde definimos estos mapeos para que seed.py y analytics_service.py los compartan?
```

**Propósito:** RF-04 / Categorización IPTC — unificar criterios entre seed y analytics.

**Archivos:**
- `backend/newsradar_api/app/seed.py:26-39` — `RSS_TO_IPTC_CATEGORY`
- `backend/newsradar_api/app/services/analytics_service.py:133-170` — `_IPTC_ID_TO_NAME`, `_RSS_TO_IPTC_NAME`, `_IPTC_NAME_TO_RSS`
- `services/notification_daemon/app/rss_processor.py:124-154` — `_RSS_CATEGORY_TO_IPTC`

**Resultado:** Mapeos duplicados pero coherentes en seed, analytics_service y daemon, cada uno optimizado para su contexto.

---

### 1.3 Diagnóstico y reparación del flujo wordcloud

```
El wordcloud global se actualiza pero el de economía no. Traza el flujo completo
desde que el daemon recibe la noticia hasta que aparece en una nube. Verifica
categorías en MongoDB y comprueba cómo se hace el match.
```

**Propósito:** Depuración del pipeline datos → nube de palabras.

**Archivos:**
- `backend/newsradar_api/app/services/analytics_service.py:360-374` — filtrado por `cloud_category`
- `frontend/src/pages/resumen/nubes.jsx:137-162` — `getBackendSlug`

**Resultado:** Detectado bug en frontend: `getBackendSlug` no reconocía nombres IPTC completos y mapeaba todo a "national". Corregido usando IDs numéricos IPTC como slugs.

---

### 1.4 Arquitectura de dual DB (Postgres + Mongo)

```
El proyecto usa PostgreSQL para entidades (usuarios, roles, alertas, fuentes)
y MongoDB para contenido (notificaciones, artículos, caches).
¿Debemos mantener esta separación o unificarlo todo en Postgres con JSONB?
```

**Propósito:** Decisión arquitectónica documentada en ADR-001.

**Archivos:**
- `docs/adr/001-stack-tecnologico.md` — justificación de la decisión
- `backend/newsradar_api/app/database.py` — conexión asyncpg
- `backend/newsradar_api/app/database_mongodb.py` — conexión motor

**Resultado:** Se mantiene dual DB. Postgres para datos relacionales con joins; Mongo para documentos grandes (noticias, caches) por su mejor rendimiento en lecturas de texto completo y agregaciones.

---

## 2. Backend Dev

Rol: implementación de funcionalidades, corrección de bugs, refactorización.

### 2.1 Añadir `_match_category` al procesador RSS del daemon

```
El daemon filtra noticias por descriptor O categoría. La categoría llega como
código IPTC (ej: "5") y label (ej: "Artes, cultura, entretenimiento y medios").
Necesito que también matchee contra el nombre español del canal RSS.
Añade _RSS_CATEGORY_TO_IPTC y _match_category().
```

**Propósito:** RF-03 / RF-04 — asegurar que el daemon clasifica usando el nombre del canal, no solo el código numérico.

**Archivos:**
- `services/notification_daemon/app/rss_processor.py:124-168` — `_RSS_CATEGORY_TO_IPTC`, `_IPTC_LABEL_TO_RSS_CATEGORIES`, `_match_category()`
- `services/notification_daemon/app/daemon.py:280-285` — pasar `category_labels` a `matches_alert`

**Resultado:** El daemon ahora matchea correctamente alertas contra canales RSS usando el label IPTC (ej: "Artes, cultura, entretenimiento y medios" → canales "Cultura" y "Entretenimiento").

---

### 2.2 Fallback a `news` collection en `build_wordcloud`

```
Si no hay notificaciones en MongoDB, el wordcloud se queda vacío.
Añade un fallback a la colección `news` para que el worker RSS
también pueda poblar las nubes.
```

**Propósito:** Robustez — asegurar que el wordcloud nunca se quede vacío.

**Archivos:**
- `backend/newsradar_api/app/services/analytics_service.py:305-310`

**Resultado:** Si `notifications` no tiene datos, se consulta `news` como alternativa.

---

### 2.3 Reducir TTL de caché wordcloud de 6h a 1h

```
La caché del wordcloud tiene TTL de 6 horas. Al probar cambios,
tarda demasiado en reflejar datos nuevos. Bájalo a 1 hora.
```

**Propósito:** Mejora de experiencia en desarrollo.

**Archivos:**
- `backend/newsradar_api/app/services/analytics_service.py:266`

**Resultado:** TTL reducido. Los resultados vacíos ya no se cachean.

---

### 2.4 Eliminar `newsradar.local` del seed

```
El seed.py tiene un bloque que crea canales "newsradar.local" como fallback
cuando no encuentra canales reales. Esto contamina la BD con datos fantasma.
Elimínalo.
```

**Propósito:** Calidad de datos — evitar canales fantasma en BD.

**Archivos:**
- `backend/newsradar_api/app/seed.py` — eliminado bloque `newsradar.local`

**Resultado:** Seed más limpio, solo canales de fuentes reales.

---

### 2.5 Limpieza de MongoDB tras cambios

```
Limpia las colecciones de MongoDB que contengan datos obsoletos:
wordcloud_cache, notifications, stats. Queremos partir de cero con
los nuevos mapeos de categorías.
```

**Propósito:** Mantenimiento — datos consistentes tras migración.

**Comando ejecutado:**
```python
await db.wordcloud_cache.delete_many({})  # 3 docs
await db.notifications.delete_many({})    # 55 docs
await db.stats.delete_many({})            # 36 docs
```

**Resultado:** 94 documentos eliminados, sistema listo para datos frescos.

---

## 3. Frontend Lead

Rol: arquitectura de componentes, diseño de interfaz, estado global, i18n.

### 3.1 Diseño del componente Nubes con subcomponentes

```
Diseña la página de nubes de palabras con:
- Una nube global (términos más frecuentes)
- Nubes por categoría IPTC (una tarjeta por categoría)
- Botón de actualizar que refresque todos los datos
- Estado de carga con skeleton
- Estado vacío con enlace a crear alerta
- Internacionalización (ES/EN)
```

**Propósito:** RF-07 / Nubes de palabras — arquitectura de componentes.

**Archivos:**
- `frontend/src/pages/resumen/nubes.jsx` — `WordCloud`, `CategoriaCloud`, `Nubes`
- `frontend/src/pages/resumen/nubes.module.css` — estilos
- `frontend/src/context/AuthContext.jsx:52-62` — `fetchNubeGlobal`, `fetchNubeCategoria`

**Resultado:** Componentes modulares: `WordCloud` (renderiza términos con tamaños proporcionales), `CategoriaCloud` (llamada individual a API), `Nubes` (orquestación con estado de carga/error/vacío).

---

### 3.2 Mapeo de slugs frontend → backend

```
Las categorías llegan desde GET /api/v1/categories con nombres IPTC completos
como "Economía, negocios y finanzas". El backend espera slugs como "economy".
Diseña el mapeo en getBackendSlug.
```

**Propósito:** RF-04 / Consistencia entre frontend y backend.

**Archivos:**
- `frontend/src/pages/resumen/nubes.jsx:137-162` — `getBackendSlug`

**Resultado:** Inicialmente se usaron slugs ingleses (politics, economy, ...), luego se migró a IDs numéricos IPTC (1000000, 4000000, ...) para evitar colisiones entre categorías que comparten slug.

---

### 3.3 Diseño del selector de categorías IPTC en alertas

```
El formulario de creación de alertas debe permitir seleccionar
UNA categoría IPTC nivel 1 de entre las 17 disponibles.
Propón un diseño: ¿radio buttons, dropdown, tarjetas?
```

**Propósito:** RF-03 / UX para selección de categoría.

**Archivos:**
- `frontend/src/pages/alerts/alerts.jsx:553-566`

**Resultado:** Radio buttons con loading desde API, búsqueda por nombre, y validación de selección única.

---

## 4. Frontend Dev

Rol: implementación de componentes, corrección de bugs, integración con API.

### 4.1 Migrar slugs de nombres ingleses a IDs IPTC

```
El getBackendSlug devuelve slugs ingleses como "politics" o "economy".
Pero necesitamos que cada categoría IPTC tenga su propia nube, sin compartir slug.
Cambia el slug para que sea el ID numérico de la categoría (cat.id).
```

**Propósito:** RF-04 / Una nube por categoría IPTC.

**Archivos:**
- `frontend/src/pages/resumen/nubes.jsx:137-162`

**Resultado:** `getBackendSlug` ahora devuelve `String(cat.id)` (ej: "4000000"). El backend filtra por ID IPTC en lugar de slug inglés.

---

### 4.2 Añadir iptcMap para nombres IPTC completos

```
Las categorías de GET /api/v1/categories tienen nombres como
"Economía, negocios y finanzas". Añade un mapa de nombres IPTC a slugs
en getBackendSlug para cubrir todas las 17 categorías.
```

**Propósito:** RF-04 / Cobertura completa de categorías.

**Archivos:**
- `frontend/src/pages/resumen/nubes.jsx` — `iptcMap` añadido (luego reemplazado por IDs)

**Resultado:** Solución intermedia. Posteriormente reemplazada por IDs numéricos.

---

### 4.3 Traducciones de categorías ES ↔ EN

```
Añade las 17 categorías IPTC a los archivos de traducción
ES/EN para que se muestren correctamente en las tarjetas de nubes
y en el dashboard.
```

**Propósito:** RNF-07.3 / Internacionalización completa.

**Archivos:**
- `frontend/public/locales/en/translation.json` — claves `categorias.*`
- `frontend/public/locales/es/translation.json` — claves `categorias.*`

**Resultado:** Las 17 categorías traducidas en ambos idiomas.

---

## 5. QA

Rol: verificación de calidad, ejecución de tests, linting, cobertura.

### 5.1 Ejecución de tests unitarios post-cambios

```
Ejecuta los tests del backend con pytest, con cobertura,
y verifica que no se rompa nada tras los cambios en analytics_service.
```

**Propósito:** RNF-04 / Regresión.

**Comando:**
```bash
DATABASE_URL="postgresql+asyncpg://newsuser:newspassword@localhost:5432/newsradar_db"
MONGODB_URL="mongodb://admin:adminpassword@localhost:27017"
ENV=testing python3 -m pytest backend/tests/ -v --cov=backend/newsradar_api --cov-report=term
```

**Resultado:** 12 tests de cloud/analytics/dashboard pasan. Tests de Postgres fallan por credenciales incorrectas en el entorno (pre-existente).

---

### 5.2 Verificación de lint (ruff + flake8)

```
Pasa ruff y flake8 sobre analytics_service.py y main.py
para asegurar que el código nuevo cumple las convenciones del proyecto.
```

**Propósito:** RNF-04 / Calidad de código.

**Comandos:**
```bash
ruff check backend/newsradar_api/app/services/analytics_service.py
flake8 backend/newsradar_api/app/services/analytics_service.py --max-line-length=120
```

**Resultado:** Todos los checks pasan. Sin errores.

---

### 5.3 Verificación de datos en MongoDB post-limpieza

```
Verifica que las notificaciones de MongoDB tienen las categorías correctas
tras la limpieza y regeneración.
```

**Propósito:** Validación de integridad de datos.

**Comando:**
```python
docs = await db.notifications.find().sort('_id', -1).to_list(length=3)
for d in docs:
    cats = [n.get('category','?') for n in d.get('news',[])[:3]]
    print(f'Notif #{d["_id"]}: alert_id={d["alert_id"]}, categories={cats}')
```

**Resultado:** Categorías correctas: `['Politica', 'Economia', 'Economia']`.

---

### 5.4 Auditoría de requisitos

```
Verifica si cada uno de los 40 requisitos del proyecto está implementado.
Busca en el código fuente evidencia de cada funcionalidad.
Devuelve una tabla con estado (✅/⚠️/❌) y referencias a archivos.
```

**Propósito:** RNF-04 / Trazabilidad requisitos-código.

**Resultado:** 34/40 requisitos implementados, 4 parciales, 2 no cumplidos. Documentado en `docs/trazabilidad.md`.

---

## 6. Scrum Master

Rol: planificación de sprints, seguimiento de tareas, documentación, coordinación.

### 6.1 Creación de AGENTS.md con guía del proyecto

```
Crea un archivo AGENTS.md en la raíz del proyecto con:
- Comandos de desarrollo (dev, test, lint, docs)
- Arquitectura del proyecto
- Servicios clave y sus responsabilidades
- Convenciones de código
- Información sobre testing y CI/CD
```

**Propósito:** RNF-09 / Documentación del repositorio.

**Archivos:**
- `AGENTS.md` — guía completa para onboarding

**Resultado:** Documento de referencia único con toda la información necesaria para que cualquier desarrollador (humano o IA) entienda el proyecto en minutos.

---

### 6.2 Mantenimiento del todolist de tareas

```
Mantén un todo list actualizado con el estado de cada tarea del sprint.
Al completar una tarea, muévela a completed. Al empezar una nueva,
ponla como in_progress. Documenta blockers.
```

**Propósito:** Seguimiento del sprint.

**Herramienta:** `todowrite` — 15 tareas gestionadas durante la sesión.

**Resultado:** Trazabilidad completa del sprint: qué se hizo, en qué orden, qué quedó bloqueado.

---

### 6.3 Planificación de feature flags

```
Documenta cómo implementar FEATURE_FLAG_WORDCLOUD y FEATURE_FLAG_BILINGUAL
en el proyecto: qué archivos tocar, cómo afectan al flujo,
y cómo se despliegan.
```

**Propósito:** Planificación técnica.

**Archivos:**
- `docs/implementar-feature-flags.md`

**Resultado:** Guía de implementación lista para el equipo.

---

### 6.4 Cronograma de entregables

```
Organiza el trabajo pendiente en un plan con:
- Prioridades (alta/media/baja)
- Dependencias entre tareas
- Estimaciones de esfuerzo
- Criterios de aceptación
```

**Propósito:** Planificación del roadmap.

**Archivos:**
- `ROADMAP.md`

**Resultado:** Roadmap actualizado con hitos y dependencias.

---

## 7. DevOps

Rol: CI/CD, contenerización, despliegue, infraestructura.

### 7.1 Añadir token a checkout steps en workflows

```
Los workflows de GitHub Actions fallan porque actions/checkout@v4
no tiene token en entornos restringidos. Añade token: ${{ secrets.GITHUB_TOKEN }}
a todos los steps de checkout.
```

**Propósito:** RNF-08 / CI/CD funcionando.

**Archivos:**
- `.github/workflows/ci.yml`
- `.github/workflows/docker.yml`
- `.github/workflows/python_tests.yml`

**Resultado:** Los 3 workflows ahora usan `token: ${{ secrets.GITHUB_TOKEN }}` en cada `actions/checkout@v4`.

---

### 7.2 Eliminar paso Deploy de cd.yml

```
El paso 'Deploy' en cd.yml ejecuta 'docker compose up -d' en el runner de GitHub,
que no tiene acceso al .env necesario. Elimínalo para que el workflow no falle.
```

**Propósito:** RNF-08 / Pipeline de despliegue funcional.

**Archivos:**
- `.github/workflows/cd.yml` — eliminado paso `Deploy`

**Resultado:** cd.yml construye y publica imágenes en GHCR sin intentar desplegar en el runner.

---

### 7.3 Extensión del servidor mock RSS

```
Añade 8 nuevas categorías al mock RSS server (Culture, Health, Society,
World, Science, Lifestyle, Entertainment, Education) con sus rutas XML
y templates de artículos. Actualiza rss_sources.json con los canales mock.
```

**Propósito:** RF-05 / Datos de prueba para todas las categorías.

**Archivos:**
- `services/mock_rss/server.py` — 12 rutas XML con templates por categoría
- `data/rss_sources.json` — canales mock para todas las categorías

**Resultado:** Mock RSS sirve feeds para 12 categorías con artículos realistas (titulares + descripciones con palabras clave del dominio).

---

### 7.4 Creación de docker-compose.dev.yml

```
Crea un docker-compose.dev.yml con hot reload para desarrollo:
- Volúmenes bind-mount para backend y frontend
- Variables de entorno para desarrollo
- Dependencias entre servicios
- Healthchecks
```

**Propósito:** RNF-06 / Entorno de desarrollo reproducible.

**Archivos:**
- `docker-compose.dev.yml`

**Resultado:** `docker compose -f docker-compose.dev.yml up --build` levanta todo el stack con hot reload.

---

### 7.5 Verificación de infraestructura

```
Verifica que los contenedores de Docker están funcionando:
PostgreSQL, MongoDB, API, Frontend y Daemon.
Comprueba que los healthchecks pasan y los puertos están expuestos.
```

**Propósito:** RNF-06 / Salud del sistema.

**Comando:**
```bash
docker ps
```

**Resultado:** 5 contenedores activos, todos con estado "Up" y healthchecks pasando.

---

> **Última actualización:** 2026-05-24
> **Total entradas:** 21 prompts documentados
> **Roles cubiertos:** Backend Lead (4), Backend Dev (5), Frontend Lead (3), Frontend Dev (3), QA (4), Scrum Master (4), DevOps (5)
