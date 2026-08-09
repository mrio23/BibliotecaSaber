from database.connection import get_connection
from sqlalchemy import text


# ============================================================
# LIVROS
# ============================================================

def cadastrar_livro(titulo, autor, ano_publicacao, quantidade):
    with get_connection() as conexao:

        conexao.execute(
            text("""
                INSERT INTO livros
                (
                    titulo,
                    autor,
                    ano_publicacao,
                    quantidade
                )
                VALUES
                (
                    :titulo,
                    :autor,
                    :ano_publicacao,
                    :quantidade
                )
            """),
            {
                "titulo": titulo,
                "autor": autor,
                "ano_publicacao": ano_publicacao,
                "quantidade": quantidade
            }
        )

        conexao.commit()


def listar_livros():
    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT *
                FROM livros
                ORDER BY id
            """)
        )

        return resultado.fetchall()

def listar_alunos():
    with get_connection() as conexao:
        
        lista = conexao.execute(text(
            """
            SELECT *
            FROM alunos
            ORDER BY id  
        """)
    )

    return lista.fetchall()

# ============================================================
# EMPRÉSTIMOS
# ============================================================

def registrar_emprestimo(
    nome_livro,
    nome_aluno,
    data_emprestimo,
    data_devolucao
):

    with get_connection() as conexao:

        # ----------------------------------------------------
        # Procurar o livro pelo título
        # ----------------------------------------------------

        livro = conexao.execute(
            text("""
                SELECT id
                FROM livros
                WHERE LOWER(titulo) = LOWER(:titulo)
            """),
            {
                "titulo": nome_livro
            }
        ).fetchone()

        if livro is None:
            raise ValueError(
                "Livro não encontrado."
            )

        # ----------------------------------------------------
        # Procurar o aluno pelo nome
        # ----------------------------------------------------

        aluno = conexao.execute(
            text("""
                SELECT id
                FROM alunos
                WHERE LOWER(nome) = LOWER(:nome)
            """),
            {
                "nome": nome_aluno
            }
        ).fetchone()

        if aluno is None:
            raise ValueError(
                "Aluno não encontrado."
            )

        # ----------------------------------------------------
        # Registrar o empréstimo
        # ----------------------------------------------------

        conexao.execute(
            text("""
                INSERT INTO emprestimos
                (
                    livro_id,
                    aluno_id,
                    data_emprestimo,
                    data_devolucao,
                    status
                )
                VALUES
                (
                    :livro_id,
                    :aluno_id,
                    :data_emprestimo,
                    :data_devolucao,
                    :status
                )
            """),
            {
                "livro_id": livro.id,
                "aluno_id": aluno.id,
                "data_emprestimo": data_emprestimo,
                "data_devolucao": data_devolucao,
                "status": "EMPRESTADO"
            }
        )

        conexao.commit()
        
def listar_emprestimos():
    with get_connection() as conexao:
        
        resultado = conexao.execute(
            text("""
                 SELECT
                    e.id,
                    l.titulo AS livro,
                    a.nome AS aluno,
                    e.data_emprestimo,
                    e.data_devolucao,
                    e.status
                FROM emprestimos e
                INNER JOIN livros l
                    ON e.livros_id = l.id
                INNER JOIN alunos a
                    ON e.aluno_id = a.id
                ORDER BY e.data_emprestimo DESC
            """)
        )
        
        return resultado.fetchall()