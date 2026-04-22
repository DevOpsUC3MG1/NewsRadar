#!/bin/bash
# scripts/seed.sh - Carga datos iniciales (medios, canales RSS, categorias)

set -e

echo "Cargando datos iniciales de RSS..."
echo ""

# Ejecutar seed.py en el contenedor
docker compose exec -T api python -m app.seed

echo ""
echo "OK - Seeding completado"
