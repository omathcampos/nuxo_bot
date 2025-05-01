-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    data_cadastro TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de gastos
CREATE TABLE IF NOT EXISTS gastos (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES usuarios(id),
    valor DECIMAL(10,2) NOT NULL,
    forma_pagamento TEXT NOT NULL,
    parcelas INTEGER,
    categoria TEXT NOT NULL,
    local TEXT NOT NULL,
    data DATE NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para melhorar performance de consultas
CREATE INDEX IF NOT EXISTS idx_gastos_usuario_id ON gastos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_gastos_data ON gastos(data);
CREATE INDEX IF NOT EXISTS idx_gastos_forma_pagamento ON gastos(forma_pagamento);

-- Função para criar índice de texto completo (opcional, para buscas avançadas)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_gastos_local_trgm ON gastos USING gin (local gin_trgm_ops);

-- Políticas de segurança RLS (Row Level Security)
-- Habilitar RLS nas tabelas
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE gastos ENABLE ROW LEVEL SECURITY;

-- Criar políticas para usuários autenticados
CREATE POLICY usuarios_policy ON usuarios
    USING (auth.uid() IS NOT NULL);

CREATE POLICY gastos_policy ON gastos
    USING (auth.uid() IS NOT NULL); 