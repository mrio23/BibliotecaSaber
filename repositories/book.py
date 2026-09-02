from database.connection import get_connection
from sqlalchemy import text
from .audit import registrar_auditoria


def cadastrar_livro(
    titulo,
    autor,
    ano_publicacao,
    quantidade
):

    with get_connection() as conexao:

        try:

            resultado = conexao.execute(
                text("""
                    INSERT INTO livros (
                        titulo,
                        autor,
                        ano_publicacao,
                        quantidade
                    )
                    VALUES (
                        :titulo,
                        :autor,
                        :ano_publicacao,
                        :quantidade
                    )
                    RETURNING id
                """),
                {
                    "titulo": titulo,
                    "autor": autor,
                    "ano_publicacao": ano_publicacao,
                    "quantidade": quantidade
                }
            )

            livro_id = resultado.scalar_one()

            # Registrar auditoria
            registrar_auditoria(
                conexao,
                "LIVRO_CADASTRADO",
                "livros",
                livro_id,
                {
                    "titulo": titulo,
                    "autor": autor,
                    "ano_publicacao": ano_publicacao,
                    "quantidade": quantidade
                }
            )

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise
        

def listar_livros():

    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT *
                FROM livros
                ORDER BY titulo
            """)
        )

        return resultado.fetchall()

def livro_possui_emprestimos(livro_id):

    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT COUNT(*)
                FROM emprestimos
                WHERE livro_id = :livro_id
            """),
            {
                "livro_id": livro_id
            }
        )

        quantidade = resultado.scalar_one()

        return int(quantidade) > 0


def excluir_livro(livro_id):

    with get_connection() as conexao:

        try:

            # Buscar livro

            livro = conexao.execute(
                text("""
                    SELECT
                        id,
                        titulo,
                        autor,
                        ano_publicacao,
                        quantidade
                    FROM livros
                    WHERE id = :livro_id
                """),
                {
                    "livro_id": livro_id
                }
            ).fetchone()

            if livro is None:

                raise ValueError(
                    "Livro não encontrado no sistema."
                )

            (
                livro_id,
                titulo,
                autor,
                ano_publicacao,
                quantidade
            ) = livro

            # Verificar empréstimos

            quantidade_emprestimos = conexao.execute(
                text("""
                    SELECT COUNT(*)
                    FROM emprestimos
                    WHERE livro_id = :livro_id
                """),
                {
                    "livro_id": livro_id
                }
            ).scalar_one()

            if quantidade_emprestimos > 0:

                raise ValueError(
                    "Não é possível excluir este livro porque "
                    "ele possui registros de empréstimos."
                )

            # Registrar auditoria

            registrar_auditoria(
                conexao,
                "LIVRO_EXCLUIDO",
                "livros",
                livro_id,
                {
                    "titulo": titulo,
                    "autor": autor,
                    "ano_publicacao": ano_publicacao,
                    "quantidade": quantidade
                }
            )

            # Excluir livro

            resultado = conexao.execute(
                text("""
                    DELETE FROM livros
                    WHERE id = :livro_id
                """),
                {
                    "livro_id": livro_id
                }
            )

            if resultado.rowcount == 0:

                raise ValueError(
                    "Livro não encontrado no sistema."
                )

            # Confirmar operação

            conexao.commit()

        except Exception:

            conexao.rollback()

            raise
