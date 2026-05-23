#!/bin/bash
# Genera documentación técnica automática con pdoc
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Generando documentación API con pdoc ==="

cd "$PROJECT_ROOT"

# Asegurar que backend está en PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

# Instalar pdoc si no está disponible
pip install pdoc -q

# Generar documentación en docs/api/ (solo app — excluye init_db y test_gmail)
pdoc newsradar_api.app -o docs/api/ --docformat google

echo "=== Documentación generada en docs/api/ ==="
echo "Abre docs/api/index.html en tu navegador"
