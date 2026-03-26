# 🗄️ Modelo de Datos - NEWSRADAR

Este documento describe la arquitectura de datos del proyecto NewsRadar, basada en una persistencia políglota para optimizar la gestión de usuarios y el gran volumen de noticias.

---

## 🐘 1. Base de Datos Relacional (PostgreSQL)
Se utiliza para datos con alta integridad referencial: usuarios, roles, configuración de alertas y registro de notificaciones.

### 👥 Módulo de Usuarios
| Tabla | Campo | Tipo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`roles`** | `id` | SERIAL | PK | ID del rol. |
| | `nombre` | VARCHAR(20) | UNIQUE, NOT NULL | "Gestor" o "Lector". |
| **`users`** | `id` | UUID | PK, DEFAULT gen_random_uuid() | ID único de usuario. |
| | `email` | VARCHAR(255) | UNIQUE, NOT NULL | Correo de acceso. |
| | `password_hash` | TEXT | NOT NULL | Contraseña (Bcrypt). |
| | `rol_id` | INT | FK -> `roles.id` | Nivel de acceso. |
| | `esta_verificado`| BOOLEAN | DEFAULT FALSE | Estado de cuenta. |

### 📢 Módulo de Alertas y Fuentes
| Tabla | Campo | Tipo | Restricciones | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`sources`** | `id` | SERIAL | PK | ID de la fuente. |
| | `medio` | VARCHAR(100) | NOT NULL | Ej: "El País", "BOE". |
| | `url_rss` | TEXT | UNIQUE, NOT NULL | URL del feed XML. |
| | `categoria_iptc` | VARCHAR(50) | NOT NULL | Categoría principal. |
| **`alerts`** | `id` | UUID | PK | ID de la alerta. |
| | `user_id` | UUID | FK -> `users.id` | Creador de la alerta. |
| | `nombre` | VARCHAR(100) | NOT NULL | Alias de la alerta. |
| | `palabra_clave` | VARCHAR(100) | NOT NULL | Término de búsqueda. |
| | `sinonimos` | JSONB | NOT NULL | Array de 3-10 términos IA. |
| | `cron_expr` | VARCHAR(20) | DEFAULT '0 * * * *' | Frecuencia de ejecución. |

---

## 🍃 2. Base de Datos Documental (MongoDB)
Se utiliza la colección `news` para almacenar las noticias indexadas. Esta estructura permite búsquedas rápidas por términos y categorías sin sobrecargar la base de datos relacional.

### 📝 Colección: `news`
**Estructura del Documento:**
```json
{
  "_id": "ObjectId", 
  "titulo": "String",
  "resumen": "String",
  "url": "String",
  "fecha_publicacion": "ISODate",
  "fuente_id": "Int", // Relación con PostgreSQL (sources.id)
  "categoria_iptc": "String",
  "alertas_relacionadas": [
    "UUID", // ID de Alerta 1
    "UUID"  // ID de Alerta 2
  ],
  "metadatos": {
    "sentimiento": "String",
    "idioma": "String"
  }
}