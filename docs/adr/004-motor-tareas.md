# ADR-004: Persistencia Políglota (PostgreSQL y MongoDB)

## Estado
Aceptado

## Fecha
2026-03-28

## Contexto
NewsRadar gestiona dos dominios de datos con necesidades opuestas:
1. **Entidades del sistema:** Usuarios, roles, alertas y fuentes. Son datos altamente relacionados que requieren integridad referencial y transacciones ACID.
2. **Información capturada:** Artículos de noticias RSS. Son datos masivos (miles por día), con esquemas variables y necesidad de búsquedas rápidas por texto o agregaciones para estadísticas (nubes de palabras).

El enunciado del proyecto exige explícitamente el uso de dos gestores de datos diferenciados para estas funciones.

## Decisión
Se adopta una arquitectura de **persistencia políglota**:

- **PostgreSQL (Relacional):** Para la gestión de usuarios, roles, configuración de alertas y logs de sistema. Se utiliza por su robustez, soporte de tipos complejos y facilidad para auditorías manuales (Inspecciones INS-02 e INS-03).
- **MongoDB (Documental):** Para el almacenamiento de las noticias capturadas. Se utiliza para permitir que el esquema de la noticia sea flexible (metadatos de IA, imágenes, categorías IPTC variables) y para aprovechar el *Aggregation Pipeline* en la generación de métricas.

## Consecuencias

**Positivas:**
- **Cumplimiento normativo:** Satisfacemos el requisito del enunciado de usar dos sistemas gestores de datos.
- **Rendimiento:** Las búsquedas masivas de noticias en MongoDB no bloquean las tablas de autenticación en PostgreSQL.
- **Flexibilidad:** Si añadimos un nuevo motor de IA que extrae campos nuevos de las noticias, no necesitamos migrar el esquema de la base de datos en MongoDB.

**Negativas / Riesgos:**
- **Complejidad Operacional:** El `docker-compose.yml` debe gestionar dos motores de base de datos, aumentando el consumo de RAM del stack en unos 500MB adicionales.
- **Consistencia Eventual:** La relación entre una alerta (en PG) y sus noticias (en Mongo) debe gestionarse a nivel de aplicación, ya que no existen claves foráneas entre diferentes motores.

## Ejemplo práctico
Cuando el **Worker RSS** procesa un feed:
1. Consulta en **PostgreSQL** las alertas activas y sus términos clave.
2. Si hay coincidencia, guarda el cuerpo de la noticia en **MongoDB** incluyendo un campo `alert_id` que referencia a Postgres.
3. Para mostrar la "Nube de Palabras" (RF-08), el frontend llama a un endpoint que ejecuta un comando `aggregate` en MongoDB sobre millones de registros en milisegundos.
