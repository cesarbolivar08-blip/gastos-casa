-- ============================================================
-- GASTOS DEL HOGAR — Setup de base de datos en Supabase
-- Ejecutá este script en: Supabase > SQL Editor > New Query
-- ============================================================

-- Tabla principal de gastos
CREATE TABLE IF NOT EXISTS gastos (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    fecha       DATE NOT NULL,
    seccion     TEXT NOT NULL,
    categoria   TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    monto       NUMERIC(12, 2) NOT NULL,
    metodo      TEXT DEFAULT '',
    notas       TEXT DEFAULT ''
);

-- Tabla de presupuestos mensuales
CREATE TABLE IF NOT EXISTS presupuestos (
    id         BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    seccion    TEXT NOT NULL,
    categoria  TEXT NOT NULL,
    monto      NUMERIC(12, 2) NOT NULL,
    periodo    TEXT DEFAULT 'mensual',
    UNIQUE (seccion, categoria, periodo)
);

-- Índices para acelerar consultas por fecha y sección
CREATE INDEX IF NOT EXISTS idx_gastos_fecha   ON gastos (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_gastos_seccion ON gastos (seccion);

-- Row Level Security: dejamos todo público para uso familiar sin login
-- (Si en el futuro querés agregar login, cambiá esto)
ALTER TABLE gastos       ENABLE ROW LEVEL SECURITY;
ALTER TABLE presupuestos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Acceso total gastos"
    ON gastos FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Acceso total presupuestos"
    ON presupuestos FOR ALL USING (true) WITH CHECK (true);
