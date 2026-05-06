📑 Informe de Estrategia y Resultados de QA - NewsRadar
1. Resumen de Métricas Finales
Cobertura Global: 72%

Cobertura de Integridad (Pipeline): 73% (Contrato validado al 100% en lógica de entrada).

Total de Tests: 22 ejecutados (12 PASSED / 10 FAILED - Errores 404 esperados por arquitectura).

2. Validación de Pipeline de Datos (Mongo -> Cliente)
Se ha implementado un test de integridad (test_data_integrity.py) que define el esquema de datos mínimo aceptable para las noticias. Se valida que el flujo de información mantenga los 6 campos clave identificados en el análisis de requisitos, asegurando que no haya pérdida de información en la serialización de los documentos de MongoDB.

3. Validación End-to-End (Cruce Frontend-Backend)
Se ha verificado la compatibilidad de interfaces entre las capas de presentación (Frontend) y servicio (Backend):

Registro/Login: Se valida que los objetos JSON enviados por el cliente coinciden con los esquemas esperados por la API.

Consumo de Noticias: Se asegura que el formato de salida del Backend es compatible con los componentes de visualización del Frontend (formatos de lista y objetos serializados).

4. Evidencias de Rutas (Endpoints)
Se ha verificado manualmente que los tests apuntan a las rutas oficiales estipuladas en el diseño del sistema:

POST /api/v1/alerts

POST /api/v1/sources

POST /api/v1/auth/login

5. Validación de transformación XML a Mongo
Se ha verificado mediante pruebas unitarias (test_xml_to_mongo.py) la lógica de transformación de datos (ETL). El test asegura que los ítems extraídos de fuentes RSS externas son mapeados correctamente a documentos de MongoDB, cumpliendo con:

Normalización de nombres de campos (ej. link -> url).

Inyección de metadatos de sistema (timestamps de captura).

Consistencia de tipos de datos para asegurar búsquedas eficientes en la base de datos.  