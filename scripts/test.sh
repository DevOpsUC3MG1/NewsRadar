#!/bin/bash
# scripts/test.sh

echo "🚀 Iniciando entorno de pruebas en Docker..."
docker-compose -f docker-compose.test.yml up -d

echo "🧪 Ejecutando tests con Pytest..."
docker-compose -f docker-compose.test.yml exec backend python -m pytest tests/ -v --cov=app

echo "🧹 Limpiando entorno..."
docker-compose -f docker-compose.test.yml down