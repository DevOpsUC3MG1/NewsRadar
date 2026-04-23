# 🗄️ Modelo de Datos - NEWSRADAR

Este documento describe la arquitectura de datos del proyecto NewsRadar, basada en una persistencia políglota para optimizar la gestión de usuarios y el gran volumen de noticias.

---

## 🐘 1. Base de Datos Relacional (PostgreSQL 15+)

Se utiliza para datos con alta integridad referencial: usuarios, roles, alertas, categorías, fuentes RSS y notificaciones.

### 👥 Módulo de Usuarios

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **roles** | `id` | SERIAL | PK | ID del rol |
| | `name` | VARCHAR(100) | UNIQUE, NOT NULL | Nombre: "admin", "user", "Gestor", "Lector" |
| **users** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de usuario |
| | `email` | VARCHAR(255) | UNIQUE, NOT NULL | Email de acceso |
| | `password` | TEXT | NOT NULL | Contraseña en texto plano (no hasheada en schema) |
| | `first_name` | VARCHAR(120) | NOT NULL | Nombre |
| | `last_name` | VARCHAR(120) | NOT NULL | Apellido |
| | `organization` | VARCHAR(180) | NOT NULL | Organización |
| | `role_ids` | INTEGER[] | DEFAULT ARRAY[]::integer[] | Array de IDs de roles asignados |
| | `verification_token` | VARCHAR(255) | UNIQUE, NULL | Token de verificación de email |
| | `is_verified` | BOOLEAN | DEFAULT FALSE | Estado de verificación de cuenta |
| | `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |
| | `updated_at` | TIMESTAMP | DEFAULT NOW() | Fecha de última actualización |

### 📢 Módulo de Alertas

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **alerts** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de alerta |
| | `user_id` | INTEGER | FK → users.id | Creador de la alerta |
| | `name` | VARCHAR(200) | NOT NULL | Nombre de la alerta |
| | `descriptors` | TEXT[] | DEFAULT ARRAY[]::text[] | Array de palabras clave |
| | `categories` | JSONB | DEFAULT '[]'::jsonb | Array de categorías IPTC en formato JSON |
| | `cron_expression` | VARCHAR(120) | NOT NULL | Expresión cron para frecuencia (ej: "0 * * * *") |
| | `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

**Estructura JSONB de categories:**
```json
[
  {
    "code": "01000000",
    "label": "Economía"
  },
  {
    "code": "02000000",
    "label": "Política"
  }
]
```

### 📂 Módulo de Categorías

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **categories** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de categoría |
| | `name` | VARCHAR(120) | NOT NULL | Nombre de categoría (ej: "Tecnología") |
| | `source` | VARCHAR(10) | DEFAULT 'IPTC' | Fuente de clasificación (siempre "IPTC") |

### 📡 Módulo de Fuentes RSS

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **information_sources** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de fuente |
| | `name` | VARCHAR(120) | NOT NULL | Nombre del medio (ej: "El País") |
| | `url` | TEXT | NOT NULL | URL de la fuente |
| **rss_channels** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de canal RSS |
| | `information_source_id` | INTEGER | FK → information_sources.id | Fuente a la que pertenece |
| | `url` | TEXT | NOT NULL | URL del feed RSS |
| | `category_id` | INTEGER | FK → categories.id | Categoría IPTC |

### 🔔 Módulo de Notificaciones (PostgreSQL)

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **notifications** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de notificación |
| | `alert_id` | INTEGER | FK → alerts.id | Alerta relacionada |
| | `timestamp` | TIMESTAMP | NOT NULL | Momento de la notificación |
| | `metrics` | JSONB | DEFAULT '[]'::jsonb | Métricas asociadas |

**Estructura JSONB de metrics:**
```json
[
  {
    "name": "noticias_encontradas",
    "value": 5
  },
  {
    "name": "relevancia_promedio",
    "value": 0.85
  }
]
```

### 📊 Estadísticas

| Tabla | Campo | Tipo | Restricciones | Descripción |
|-------|-------|------|----------------|-------------|
| **stats** | `id` | INTEGER | PK, AUTOINCREMENT | ID único de estadística |
| | `metrics` | JSONB | DEFAULT '[]'::jsonb | Métricas configurables |

---

## 🍃 2. Base de Datos Documental (MongoDB 7+)

Se utiliza para almacenar notificaciones indexadas (colección `notifications`). Esta estructura permite búsquedas rápidas sin sobrecargar la base de datos relacional.

### 📝 Colección: `notifications`

**Estructura del Documento:**
```json
{
  "_id": 1,
  "alert_id": 1,
  "timestamp": "2026-04-23T10:30:00Z",
  "metrics": [
    {
      "name": "noticias_encontradas",
      "value": 5
    }
  ]
}
```

**Campos:**
- `_id` (Integer): ID único de la notificación
- `alert_id` (Integer): Referencia a la alerta en PostgreSQL
- `timestamp` (ISODate): Momento de generación
- `metrics` (Array): Lista de métricas con nombre y valor numérico

### 📰 Colección: `news` (Reservada para futuro)

Estructura preparada para almacenar noticias indexadas:
```json
{
  "_id": "ObjectId",
  "titulo": "String",
  "resumen": "String",
  "url": "String",
  "fecha_publicacion": "ISODate",
  "information_source_id": "Integer",
  "categoria_iptc": "String",
  "alertas_relacionadas": ["Integer", ...],
  "metadatos": {
    "sentimiento": "String",
    "idioma": "String"
  }
}
```

---

## 3. Relaciones Between Databases

```
PostgreSQL                          MongoDB
┌──────────────┐                   ┌──────────────┐
│ users        │                   │notifications │
├──────────────┤                   ├──────────────┤
│ id (PK)      │                   │ _id          │
│ email        │                   │ alert_id (FK)│
│ role_ids[]   │                   │ timestamp    │
└──────────────┘                   │ metrics      │
       │                           └──────────────┘
       │ 1:N                              ▲
       │                                  │
┌──────────────┐                         │ MongoDB
│ alerts       │                         │
├──────────────┤                         │
│ id (PK)      │───────────────────────┤ 1:N
│ user_id (FK) │ stores notifications  │
│ name         │
│ descriptors[]│
└──────────────┘
```

---

## 4. Migraciones (Alembic)

El proyecto usa SQLAlchemy + Alembic para control de versiones del esquema:

```
backend/migrations/
├── versions/
│   └── 001_add_verification_fields.py  # Migración: Añadir campos de verificación
├── env.py                              # Configuración de Alembic
├── script.py.mako                      # Template de migraciones
└── __init__.py
```

**Ejecutar migraciones:**
```bash
cd backend
alembic upgrade head  # Aplicar todas las migraciones pendientes
alembic downgrade -1  # Revertir última migración
```

---

## 5. Características de Persistencia

### PostgreSQL
✅ ACID transactions
✅ Integridad referencial
✅ Índices para búsquedas rápidas
✅ JSONB para flexibilidad en categorías y métricas
✅ Arrays nativos para role_ids

### MongoDB
✅ Flexibilidad en esquema
✅ Escalabilidad horizontal
✅ Búsqueda full-text
✅ Agregaciones para análisis

---

## 6. Backups y Recuperación

### PostgreSQL
```bash
docker compose exec db_postgres pg_dump -U newsradar_user newsradar_db > backup.sql
docker compose exec db_postgres psql -U newsradar_user newsradar_db < backup.sql
```

### MongoDB
```bash
docker compose exec db_mongodb mongodump --out=/backup
docker compose exec db_mongodb mongorestore /backup
```

---

## 7. Índices Recomendados

### PostgreSQL
```sql
-- Usuario
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verification_token ON users(verification_token);

-- Alertas
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_name ON alerts(name);

-- Categorías
CREATE INDEX idx_categories_name ON categories(name);

-- Canales RSS
CREATE INDEX idx_rss_channels_source_id ON rss_channels(information_source_id);
CREATE INDEX idx_rss_channels_category_id ON rss_channels(category_id);
```

### MongoDB
```javascript
db.notifications.createIndex({ "alert_id": 1 });
db.notifications.createIndex({ "timestamp": -1 });
db.notifications.createIndex({ "alert_id": 1, "timestamp": -1 });
```