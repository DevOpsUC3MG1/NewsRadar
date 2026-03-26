#!/bin/bash
echo "🚀 Iniciando construcción de NewsRadar..."

# Construir imágenes sin usar caché para asegurar limpieza
docker compose build --no-cache

echo "✅ Construcción finalizada con éxito."