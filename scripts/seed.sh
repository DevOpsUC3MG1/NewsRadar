#!/bin/bash
# scripts/seed.sh

echo "🌱 Ejecutando carga de datos iniciales..."

# Ejecutamos el script de python dentro del contenedor de la API
docker compose exec api python app/seed.py

echo "✅ Proceso de seed completado."