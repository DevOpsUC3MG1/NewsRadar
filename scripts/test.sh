#!/bin/bash
echo "🧪 Ejecutando pruebas unitarias y de integración..."

# Ejecutar pytest dentro del contenedor de la API
docker compose run --rm api pytest --cov=app --cov-report=term-missing

echo "📊 Pruebas finalizadas."