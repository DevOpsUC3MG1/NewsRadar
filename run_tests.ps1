Write-Host "🚀 Iniciando batería de tests con cobertura..." -ForegroundColor Cyan

# Ejecutar pytest con reporte de cobertura
# --cov=backend: mide el código de la carpeta backend
# --cov-report=html: genera la web interactiva
# --cov-report=term: muestra resumen en consola
python -m pytest --cov=backend --cov-report=html --cov-report=term backend/tests/

Write-Host "✅ Tests finalizados. Informe detallado en: ./htmlcov/index.html" -ForegroundColor Green