-- Script para crear el esquema de la base de datos NewsRadar
-- Ejecutar con: psql -U admin -h localhost -d newsradar_core -f create_schema.sql

-- Eliminar tablas existentes si existen (en orden correcto por dependencias)
DROP TABLE IF EXISTS rss_channels CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS information_sources CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Crear tabla de roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Crear tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(120),
    last_name VARCHAR(120),
    organization VARCHAR(180),
    password VARCHAR(128),
    role_ids JSON DEFAULT '[]'::json
);

CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_users_email ON users(email);

-- Crear tabla de alertas
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    descriptors JSON DEFAULT '[]'::json,
    categories JSON DEFAULT '[]'::json,
    cron_expression VARCHAR(120),
    information_sources_ids JSON DEFAULT '[]'::json,
    rss_channels_ids JSON DEFAULT '[]'::json,
    prioridad INTEGER,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_alerts_id ON alerts(id);
CREATE INDEX ix_alerts_user_id ON alerts(user_id);

-- Crear tabla de categorías
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120),
    source VARCHAR(10) DEFAULT 'IPTC'
);

CREATE INDEX ix_categories_id ON categories(id);

-- Crear tabla de fuentes de información
CREATE TABLE information_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120),
    url VARCHAR(500)
);

CREATE INDEX ix_information_sources_id ON information_sources(id);

-- Crear tabla de canales RSS
CREATE TABLE rss_channels (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500),
    category_id INTEGER REFERENCES categories(id),
    information_source_id INTEGER NOT NULL REFERENCES information_sources(id) ON DELETE CASCADE
);

CREATE INDEX ix_rss_channels_id ON rss_channels(id);
CREATE INDEX ix_rss_channels_information_source_id ON rss_channels(information_source_id);
CREATE INDEX ix_rss_channels_category_id ON rss_channels(category_id);

-- Insertar datos semilla
INSERT INTO roles (name) VALUES ('admin'), ('user');

INSERT INTO users (email, first_name, last_name, organization, password, role_ids)
VALUES ('admin@newsradar.com', 'Admin', 'NewsRadar', 'NewsRadar', 'admin123', '[1]'::json);

-- Verificar la creación
SELECT 'Tablas creadas correctamente' AS status;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;