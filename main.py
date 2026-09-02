import json

from database.connection import get_connection
from sqlalchemy import text

# ============================================================
# LIVROS
# ============================================================

from repositories.book import (
    cadastrar_livro,
    listar_livros,
    livro_possui_emprestimos,
    excluir_livro,
)


# ============================================================
# ALUNOS
# ============================================================

from repositories.user import (
    cadastrar_aluno,
    listar_alunos,
    aluno_possui_emprestimos,
    excluir_aluno,
)


# ============================================================
# EMPRÉSTIMOS
# ============================================================

from repositories.loan import (
    registrar_emprestimo,
    listar_emprestimos,
    registrar_devolucao,
)


# ============================================================
# AUDITORIA
# ============================================================

from repositories.audit import (
    registrar_auditoria,
    listar_auditoria,
)


# ============================================================
# DASHBOARD
# ============================================================

from repositories.dashboard import (
    contar_livros,
    contar_alunos,
    contar_emprestimos_ativos,
    contar_emprestimos_atrasados,
)