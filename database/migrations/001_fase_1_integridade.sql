-- Biblioteca Saber | Fase 1
-- Migração segura: não altera dados existentes nem cria a separação livro/exemplar ainda.
-- Execute este arquivo uma vez no PostgreSQL da aplicação.

BEGIN;

-- ============================================================
-- 1. Integridade básica do acervo
-- ============================================================

ALTER TABLE public.livros
    ALTER COLUMN titulo SET NOT NULL,
    ALTER COLUMN autor SET NOT NULL,
    ALTER COLUMN quantidade SET NOT NULL;

ALTER TABLE public.livros
    ADD CONSTRAINT livros_quantidade_nao_negativa
    CHECK (quantidade >= 0);

ALTER TABLE public.livros
    ADD CONSTRAINT livros_ano_publicacao_valido
    CHECK (
        ano_publicacao IS NULL
        OR ano_publicacao BETWEEN 1 AND EXTRACT(YEAR FROM CURRENT_DATE)::integer
    );

-- ============================================================
-- 2. Integridade básica dos alunos
-- ============================================================

ALTER TABLE public.alunos
    ALTER COLUMN nome SET NOT NULL,
    ALTER COLUMN matricula SET NOT NULL;

ALTER TABLE public.alunos
    ADD CONSTRAINT alunos_nome_nao_vazio
    CHECK (length(btrim(nome)) > 0);

ALTER TABLE public.alunos
    ADD CONSTRAINT alunos_matricula_nao_vazia
    CHECK (length(btrim(matricula)) > 0);

-- ============================================================
-- 3. Integridade dos empréstimos
-- ============================================================

ALTER TABLE public.emprestimos
    ADD CONSTRAINT emprestimos_datas_validas
    CHECK (
        data_devolucao IS NULL
        OR data_devolucao >= data_emprestimo
    );

-- ============================================================
-- 4. Índices para as consultas mais frequentes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_livros_titulo_lower
    ON public.livros (LOWER(titulo));

CREATE INDEX IF NOT EXISTS idx_livros_autor_lower
    ON public.livros (LOWER(autor));

CREATE INDEX IF NOT EXISTS idx_alunos_nome_lower
    ON public.alunos (LOWER(nome));

CREATE INDEX IF NOT EXISTS idx_emprestimos_status
    ON public.emprestimos (status);

CREATE INDEX IF NOT EXISTS idx_emprestimos_aluno_id
    ON public.emprestimos (aluno_id);

CREATE INDEX IF NOT EXISTS idx_emprestimos_livro_id
    ON public.emprestimos (livro_id);

CREATE INDEX IF NOT EXISTS idx_emprestimos_data_devolucao
    ON public.emprestimos (data_devolucao);

-- ============================================================
-- 5. Auditoria
-- ============================================================

CREATE TABLE IF NOT EXISTS public.auditoria (
    id BIGSERIAL PRIMARY KEY,
    acao VARCHAR(100) NOT NULL,
    entidade VARCHAR(100) NOT NULL,
    entidade_id INTEGER,
    dados JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_hora TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auditoria_data_hora
    ON public.auditoria (data_hora DESC);

CREATE INDEX IF NOT EXISTS idx_auditoria_entidade
    ON public.auditoria (entidade, entidade_id);

-- ============================================================
-- 6. Histórico de empréstimos
-- ============================================================

CREATE TABLE IF NOT EXISTS public.historico_emprestimos (
    id BIGSERIAL PRIMARY KEY,
    emprestimo_id INTEGER NOT NULL,
    aluno_id INTEGER,
    aluno_nome VARCHAR(100) NOT NULL,
    aluno_matricula VARCHAR(20) NOT NULL,
    livro_id INTEGER,
    livro_titulo VARCHAR(100) NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao DATE,
    status VARCHAR(30) NOT NULL,
    registrado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_historico_emprestimos_aluno
    ON public.historico_emprestimos (aluno_id);

CREATE INDEX IF NOT EXISTS idx_historico_emprestimos_livro
    ON public.historico_emprestimos (livro_id);

CREATE INDEX IF NOT EXISTS idx_historico_emprestimos_data
    ON public.historico_emprestimos (registrado_em DESC);

COMMIT;
