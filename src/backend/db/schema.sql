-- ===========================================
-- Schema do Banco de Dados
-- Hierarquia: usuarios -> bombas -> movimentacao_z
-- ===========================================

-- 1. usuarios
CREATE TABLE IF NOT EXISTS usuarios(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    updated_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
);

-- 2. bombas (entidade central)
CREATE TABLE IF NOT EXISTS bombas(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    localizacao VARCHAR(255),
    operador_id INTEGER NOT NULL,
    diametro_carretel_cm DECIMAL(6,4) NOT NULL DEFAULT 0.852,
    comprimento_corda_cm DECIMAL(8,2) NOT NULL DEFAULT 35.0,
    limite_corrente DECIMAL(12,6),              -- limite maximo de corrente em Amperes
    passo_auto_cm DECIMAL(6,2) NOT NULL DEFAULT 2.0, -- passo de descida/subida no modo auto
    created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    CONSTRAINT bombas_operador_fk
        FOREIGN KEY(operador_id) REFERENCES usuarios(id)
);



-- 3. movimentacao_z (registros de movimentos no eixo Z)
-- Migration banco existente:
--   ALTER TABLE movimentacao_z ALTER COLUMN operador_id DROP NOT NULL;
--   ALTER TABLE movimentacao_z DROP CONSTRAINT IF EXISTS movz_operador_fk;
CREATE TABLE IF NOT EXISTS movimentacao_z(
    id SERIAL PRIMARY KEY,
    bomba_id INTEGER NOT NULL,
    operador_id INTEGER,
    comando_bruto VARCHAR(255) NOT NULL,
    posicao_inicial_cm DECIMAL(8,2) NOT NULL,
    deslocamento_solicitado_cm DECIMAL(8,2) NOT NULL,
    deslocamento_real_cm DECIMAL(8,2),
    posicao_final_cm DECIMAL(8,2),
    voltas_mqtt DECIMAL(8,4) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'EM_ANDAMENTO',
    -- status valores: EM_ANDAMENTO | CONCLUIDO | ABORTADO | INTERROMPIDO | SNAPSHOT
    timestamp_inicio TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    timestamp_fim TIMESTAMP,
    CONSTRAINT movz_bomba_fk
        FOREIGN KEY(bomba_id) REFERENCES bombas(id)
);

-- 4. movimentacao_xy (registros de movimentos horizontais da balsa)
CREATE TABLE IF NOT EXISTS movimentacao_xy(
    id SERIAL PRIMARY KEY,
    bomba_id INTEGER NOT NULL,
    operador_id INTEGER NOT NULL,
    direcao VARCHAR(20) NOT NULL,           -- 'esquerda', 'direita'
    duracao_ms INTEGER,                     -- tempo que o motor ficou ativo (ms)
    status VARCHAR(50) NOT NULL DEFAULT 'EM_ANDAMENTO',  -- EM_ANDAMENTO, CONCLUIDO, INTERROMPIDO
    timestamp_inicio TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    timestamp_fim TIMESTAMP,
    CONSTRAINT movxy_bomba_fk
        FOREIGN KEY(bomba_id) REFERENCES bombas(id),
    CONSTRAINT movxy_operador_fk
        FOREIGN KEY(operador_id) REFERENCES usuarios(id)
);

-- 5. leituras_corrente (registros do sensor de corrente - módulo 1-B)
-- Migration banco existente:
--   ALTER TABLE bombas RENAME COLUMN limite_corrente TO limite_superior;
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS limite_inferior DECIMAL(12,6);
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS passo_auto_cm DECIMAL(6,2) NOT NULL DEFAULT 2.0;
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS limite_prox_frente_m DECIMAL(5,3) DEFAULT 0.30;
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS limite_prox_tras_m   DECIMAL(5,3) DEFAULT 0.30;
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS limite_prox_esq_m    DECIMAL(5,3) DEFAULT 0.30;
--   ALTER TABLE bombas ADD COLUMN IF NOT EXISTS limite_prox_dir_m    DECIMAL(5,3) DEFAULT 0.30;
CREATE TABLE IF NOT EXISTS bombas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    localizacao VARCHAR(255),
    operador_id INTEGER NOT NULL REFERENCES usuarios(id),
    diametro_carretel_cm DECIMAL(8,2) NOT NULL DEFAULT 10.0,
    comprimento_corda_cm DECIMAL(8,2) NOT NULL DEFAULT 100.0,
    limite_inferior DECIMAL(12,6),   -- corrente mínima de dragagem (abaixo = descer)
    limite_superior DECIMAL(12,6),   -- corrente máxima de proteção (acima = subir)
    passo_auto_cm DECIMAL(6,2) NOT NULL DEFAULT 2.0,
    created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
);
CREATE TABLE IF NOT EXISTS leituras_corrente(
    id SERIAL PRIMARY KEY,
    bomba_id INTEGER NOT NULL,
    operador_id INTEGER,
    corrente_a DECIMAL(12,6) NOT NULL,
    timestamp_leitura TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    CONSTRAINT lc_bomba_fk
        FOREIGN KEY(bomba_id) REFERENCES bombas(id),
    CONSTRAINT lc_operador_fk
        FOREIGN KEY(operador_id) REFERENCES usuarios(id)
);

-- 6. leituras_distancia (registros do sensor de distancia - módulo 2-C)
CREATE TABLE IF NOT EXISTS leituras_distancia(
    id SERIAL PRIMARY KEY,
    bomba_id INTEGER NOT NULL,
    operador_id INTEGER NOT NULL,
    distancia_frente_m DECIMAL(8,2) NOT NULL,
    distancia_tras_m DECIMAL(8,2) NOT NULL,
    distancia_esq_m DECIMAL(8,2) NOT NULL,
    distancia_dir_m DECIMAL(8,2) NOT NULL,
    timestamp_leitura TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'),
    CONSTRAINT ld_bomba_fk
        FOREIGN KEY(bomba_id) REFERENCES bombas(id),
    CONSTRAINT ld_operador_fk
        FOREIGN KEY(operador_id) REFERENCES usuarios(id)
);