-- Configurar la codificación de la base de datos
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

-- Crear la base de datos si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cafexport') THEN
        CREATE DATABASE cafexport WITH ENCODING 'UTF8' LC_COLLATE='es_CO.UTF-8' LC_CTYPE='es_CO.UTF-8' TEMPLATE=template0;
    END IF;
END
$$;



CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,         -- 'campesino', 'empresa', 'admin'
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE,         -- Solo para campesinos
    nit VARCHAR(20) UNIQUE,            -- Solo para empresas
    email VARCHAR(120),                
    password_hash VARCHAR(255) NOT NULL, -- Aumentamos el tamaño para el hash
    direccion_finca VARCHAR(200),      
    direccion_empresa VARCHAR(200),    
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear enum para tipo de café
CREATE TYPE tipo_cafe AS ENUM (
    'Pasilla',
    'Arabica'
);

-- Crear enum para estado de venta (si no existe)
DROP TYPE IF EXISTS estado_venta CASCADE;
CREATE TYPE estado_venta AS ENUM (
    'Pendiente',
    'Aprobada',
    'Rechazada',
    'Cancelada',
    'Completada'
);
-- Tabla de ventas
DROP TABLE IF EXISTS ventas CASCADE;
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    campesino_id INTEGER NOT NULL,
    empresa_id INTEGER,
    tipo_cafe tipo_cafe NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL CHECK (cantidad > 0),
    precio_kg DECIMAL(10,2) NOT NULL CHECK (precio_kg > 0),
    total DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * precio_kg) STORED,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado estado_venta DEFAULT 'Aprobada',
    CONSTRAINT fk_campesino FOREIGN KEY (campesino_id) 
        REFERENCES usuario(id) ON DELETE RESTRICT,
    CONSTRAINT fk_empresa FOREIGN KEY (empresa_id) 
        REFERENCES usuario(id) ON DELETE RESTRICT
);

-- Crear enum para fuente del precio
CREATE TYPE fuente_precio AS ENUM ('manual', 'bolsa_valores', 'api_externa');

-- Tabla de precios del café mejorada
CREATE TABLE IF NOT EXISTS precios_cafe (
    id SERIAL PRIMARY KEY,
    tipo_cafe tipo_cafe NOT NULL,
    precio_kg DECIMAL(10,2) NOT NULL CHECK (precio_kg > 0),
    precio_usd DECIMAL(10,2),          -- Precio en dólares de la bolsa
    tasa_cambio DECIMAL(10,2),         -- Tasa de cambio USD/COP
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fuente fuente_precio NOT NULL DEFAULT 'manual',
    activo BOOLEAN DEFAULT true,
    referencia_externa VARCHAR(100),    -- ID o referencia de la API externa
    metadata JSON,                     -- Datos adicionales de la API
    CONSTRAINT unique_tipo_activo UNIQUE (tipo_cafe, activo),
    CONSTRAINT precio_completo CHECK (
        (fuente = 'manual' AND precio_usd IS NULL AND tasa_cambio IS NULL) OR
        (fuente IN ('bolsa_valores', 'api_externa') AND precio_usd IS NOT NULL AND tasa_cambio IS NOT NULL)
    )
);

-- Tabla de reportes
CREATE TABLE IF NOT EXISTS reportes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    datos JSONB NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT fecha_valida CHECK (fecha_inicio <= fecha_fin)
);

-- Índices para optimizar consultas
CREATE INDEX idx_ventas_campesino ON ventas(campesino_id);
CREATE INDEX idx_ventas_empresa ON ventas(empresa_id);
CREATE INDEX idx_ventas_fecha ON ventas(fecha);
CREATE INDEX idx_ventas_estado ON ventas(estado);
CREATE INDEX idx_precios_activos ON precios_cafe(tipo_cafe) WHERE activo = true;
CREATE INDEX idx_reportes_usuario_fecha ON reportes(usuario_id, fecha_inicio, fecha_fin);

-- Índices adicionales para consultas con API
CREATE INDEX idx_precios_fecha ON precios_cafe(fecha_actualizacion);
CREATE INDEX idx_precios_fuente ON precios_cafe(fuente) WHERE activo = true;

-- Definir una tabla para las compras de las empresas a CafExport
CREATE TABLE IF NOT EXISTS compras_empresa (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER NOT NULL, -- La empresa que compra
    cafexport_vendedor_id INTEGER NOT NULL, -- El ID de usuario de CafExport (como vendedor)
    tipo_cafe tipo_cafe NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL CHECK (cantidad > 0),
    precio_kg DECIMAL(10,2) NOT NULL CHECK (precio_kg > 0),
    total DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * precio_kg) STORED,
    fecha_orden TIMESTAMP NOT NULL,
    fecha_entrega TIMESTAMP, -- Opcional, como en el formulario
    notas TEXT, -- Para especificaciones adicionales
    estado estado_venta DEFAULT 'Pendiente', -- Estado de la compra de la empresa
    CONSTRAINT fk_empresa_compradora FOREIGN KEY (empresa_id)
        REFERENCES usuario(id) ON DELETE RESTRICT,
    CONSTRAINT fk_cafexport_vendedor FOREIGN KEY (cafexport_vendedor_id)
        REFERENCES usuario(id) ON DELETE RESTRICT -- Asegúrate de que CafExport tenga un usuario en la tabla
);


INSERT INTO usuario (
    id,
    tipo,
    nombre,
    cedula,
    nit,
    email,
    password_hash,
    direccion_finca,
    direccion_empresa
) VALUES (
    1,
    'admin',
    'cafexport',
    NULL,
    NULL,
    'cafexport@example.com',
    '$2b$12$u4xy2X6jNjTL8JfoA9KArOzC/Io6cdmYm8/JUK2dBhGZxqpRUS33K', -- contraseña cafexport123
    NULL,
    NULL
);

