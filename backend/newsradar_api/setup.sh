#!/bin/bash

# Script de configuración automática de NewsRadar API
# Este script configura PostgreSQL, crea el usuario y la base de datos,
# e inicializa el esquema

set -e  # Salir si hay algún error

echo "======================================="
echo "NewsRadar API - Setup Automático"
echo "======================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que PostgreSQL esté corriendo
echo "Verificando PostgreSQL..."
if ! systemctl is-active --quiet postgresql; then
    echo -e "${YELLOW}PostgreSQL no está corriendo. Iniciando...${NC}"
    sudo systemctl start postgresql
    sleep 2
fi

echo -e "${GREEN}✓ PostgreSQL está corriendo${NC}"
echo ""

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres psql << EOF
-- Eliminar usuario y base de datos si existen
DROP DATABASE IF EXISTS newsradar_core;
DROP USER IF EXISTS admin;

-- Crear usuario admin
CREATE USER admin WITH PASSWORD 'password123';

-- Crear base de datos
CREATE DATABASE newsradar_core OWNER admin;

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE newsradar_core TO admin;

-- Mostrar confirmación
\echo 'Usuario y base de datos creados correctamente'
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"
echo ""

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cat > .env << EOF
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/newsradar_core

# MongoDB
MONGO_URL=mongodb://localhost:27017
EOF
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
else
    echo -e "${YELLOW}⚠ Archivo .env ya existe, no se sobrescribe${NC}"
fi
echo ""

# Verificar que MongoDB esté corriendo
echo "Verificando MongoDB..."
if ! systemctl is-active --quiet mongod; then
    echo -e "${YELLOW}MongoDB no está corriendo. Iniciando...${NC}"
    sudo systemctl start mongod
    sleep 2
fi

echo -e "${GREEN}✓ MongoDB está corriendo${NC}"
echo ""

# Verificar que el entorno virtual esté activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}✗ Entorno virtual no activado${NC}"
    echo "Por favor ejecuta: source .venv/bin/activate"
    exit 1
fi

echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Instalar dependencias si es necesario
echo "Verificando dependencias..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Inicializar base de datos
echo "Inicializando esquema de base de datos..."
export PYTHONPATH=$PYTHONPATH:.
python -m init_db

echo "Ejecutando seed de datos iniciales..."
python -m app.seed

echo ""
echo "======================================="
echo -e "${GREEN}✅ Setup completado exitosamente!${NC}"
echo "======================================="
echo ""
echo "Para iniciar la aplicación, ejecuta:"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Credenciales de acceso:"
echo "  Email: admin@newsradar.com"
echo "  Password: admin123"
echo ""
echo "Documentación API:"
echo "  http://127.0.0.1:8000/docs"
echo ""