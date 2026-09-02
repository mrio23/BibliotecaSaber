from database.connection import get_connection
from sqlalchemy import text
from .audit import registrar_auditoria

def cadastrar_aluno(nome, matricula):

    with get_connection() as conexao:

        try:

            resultado = conexao.execute(
                text("""
                    INSERT INTO alunos (
                        nome,
                        matricula
                    )
                    VALUES (
                        :nome,
                        :matricula
                    )
                    RETURNING id
                """),
                {
                    "nome": nome,
                    "matricula": matricula
                }
            )

            aluno_id = resultado.scalar_one()

            # Registrar auditoria
            registrar_auditoria(
                conexao,
                "ALUNO_CADASTRADO",
                "alunos",
                aluno_id,
                {
                    "nome": nome,
                    "matricula": matricula
                }
            )

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise


def listar_alunos():

    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT *
                FROM alunos
                ORDER BY nome
            """)
        )

        return resultado.fetchall()


def aluno_possui_emprestimos(aluno_id):

    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT COUNT(*)
                FROM emprestimos
                WHERE aluno_id = :aluno_id
                AND status = 'ATIVO'
            """),
            {
                "aluno_id": aluno_id
            }
        )

        quantidade = resultado.scalar_one()

        return int(quantidade) > 0


# ============================================================
# EXCLUIR ALUNO
# ============================================================

def excluir_aluno(aluno_id):

    with get_connection() as conexao:

        try:

            # ------------------------------------------------
            # 1. Buscar aluno
            # ------------------------------------------------

            aluno = conexao.execute(
                text("""
                    SELECT
                        id,
                        nome,
                        matricula
                    FROM alunos
                    WHERE id = :aluno_id
                """),
                {
                    "aluno_id": aluno_id
                }
            ).fetchone()

            if aluno is None:
                raise ValueError(
                    "Aluno não encontrado no sistema."
                )

            aluno_id, nome, matricula = aluno


            # ------------------------------------------------
            # 2. Buscar empréstimos
            # ------------------------------------------------

            emprestimos = conexao.execute(
                text("""
                    SELECT
                        e.id,
                        e.livro_id,
                        l.titulo,
                        e.data_emprestimo,
                        e.data_devolucao,
                        e.status
                    FROM emprestimos e
                    JOIN livros l
                        ON l.id = e.livro_id
                    WHERE e.aluno_id = :aluno_id
                """),
                {
                    "aluno_id": aluno_id
                }
            ).fetchall()


            # ------------------------------------------------
            # 3. Salvar empréstimos no histórico
            # ------------------------------------------------

            for emprestimo in emprestimos:

                (
                    emprestimo_id,
                    livro_id,
                    livro_titulo,
                    data_emprestimo,
                    data_devolucao,
                    status
                ) = emprestimo

                conexao.execute(
                    text("""
                        INSERT INTO historico_emprestimos (
                            emprestimo_id,
                            aluno_id,
                            aluno_nome,
                            aluno_matricula,
                            livro_id,
                            livro_titulo,
                            data_emprestimo,
                            data_devolucao,
                            status
                        )
                        VALUES (
                            :emprestimo_id,
                            :aluno_id,
                            :aluno_nome,
                            :aluno_matricula,
                            :livro_id,
                            :livro_titulo,
                            :data_emprestimo,
                            :data_devolucao,
                            :status
                        )
                    """),
                    {
                        "emprestimo_id": emprestimo_id,
                        "aluno_id": aluno_id,
                        "aluno_nome": nome,
                        "aluno_matricula": matricula,
                        "livro_id": livro_id,
                        "livro_titulo": livro_titulo,
                        "data_emprestimo": data_emprestimo,
                        "data_devolucao": data_devolucao,
                        "status": status
                    }
                )


            # ------------------------------------------------
            # 4. Registrar auditoria
            # ------------------------------------------------

            registrar_auditoria(
                conexao,
                "ALUNO_EXCLUIDO",
                "alunos",
                aluno_id,
                {
                    "nome": nome,
                    "matricula": matricula,
                    "quantidade_emprestimos": len(emprestimos)
                }
            )


            # ------------------------------------------------
            # 5. Excluir empréstimos
            # ------------------------------------------------

            conexao.execute(
                text("""
                    DELETE FROM emprestimos
                    WHERE aluno_id = :aluno_id
                """),
                {
                    "aluno_id": aluno_id
                }
            )


            # ------------------------------------------------
            # 6. Excluir aluno
            # ------------------------------------------------

            resultado = conexao.execute(
                text("""
                    DELETE FROM alunos
                    WHERE id = :aluno_id
                """),
                {
                    "aluno_id": aluno_id
                }
            )

            if resultado.rowcount == 0:
                raise ValueError(
                    "Aluno não encontrado no sistema."
                )


            # ------------------------------------------------
            # 7. Confirmar
            # ------------------------------------------------

            conexao.commit()

        except Exception:

            conexao.rollback()

            raise