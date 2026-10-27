from database.connection import get_connection
from sqlalchemy import text
from .audit import registrar_auditoria

def registrar_emprestimo(
    nome_livro,
    nome_aluno,
    data_emprestimo,
    data_devolucao
):

    with get_connection() as conexao:

        try:

            # ------------------------------------------------
            # Procurar livro
            # ------------------------------------------------

            livro = conexao.execute(
                text("""
                    SELECT
                        id,
                        titulo,
                        quantidade
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


            livro_id, livro_titulo, quantidade = livro


            # ------------------------------------------------
            # Verificar disponibilidade
            # ------------------------------------------------

            if quantidade <= 0:

                raise ValueError(
                    "Este livro não possui exemplares disponíveis."
                )


            # ------------------------------------------------
            # Procurar aluno
            # ------------------------------------------------

            aluno = conexao.execute(
                text("""
                    SELECT
                        id,
                        nome,
                        matricula
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


            aluno_id, aluno_nome, matricula = aluno


            # ------------------------------------------------
            # Registrar empréstimo
            # ------------------------------------------------

            resultado = conexao.execute(
                text("""
                    INSERT INTO emprestimos (
                        livro_id,
                        aluno_id,
                        data_emprestimo,
                        data_devolucao,
                        status
                    )
                    VALUES (
                        :livro_id,
                        :aluno_id,
                        :data_emprestimo,
                        :data_devolucao,
                        :status
                    )
                    RETURNING id
                """),
                {
                    "livro_id": livro_id,
                    "aluno_id": aluno_id,
                    "data_emprestimo": data_emprestimo,
                    "data_devolucao": data_devolucao,
                    "status": "ATIVO"
                }
            )

            emprestimo_id = resultado.scalar_one()


            # ------------------------------------------------
            # Diminuir quantidade disponível
            # ------------------------------------------------

            conexao.execute(
                text("""
                    UPDATE livros
                    SET quantidade = quantidade - 1
                    WHERE id = :livro_id
                """),
                {
                    "livro_id": livro_id
                }
            )


            # ------------------------------------------------
            # Registrar auditoria
            # ------------------------------------------------

            registrar_auditoria(
                conexao,
                "EMPRESTIMO_REGISTRADO",
                "emprestimos",
                emprestimo_id,
                {
                    "aluno_id": aluno_id,
                    "aluno_nome": aluno_nome,
                    "aluno_matricula": matricula,
                    "livro_id": livro_id,
                    "livro_titulo": livro_titulo,
                    "data_emprestimo": data_emprestimo,
                    "data_devolucao": data_devolucao,
                    "status": "ATIVO"
                }
            )


            # ------------------------------------------------
            # Confirmar
            # ------------------------------------------------

            conexao.commit()


        except Exception:

            conexao.rollback()

            raise


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
                    ON e.livro_id = l.id
                INNER JOIN alunos a
                    ON e.aluno_id = a.id
                ORDER BY e.data_emprestimo DESC
            """)
        )

        return resultado.fetchall()


# ============================================================
# DEVOLUÇÃO
# ============================================================

def registrar_devolucao(emprestimo_id):

    with get_connection() as conexao:

        try:

            # ------------------------------------------------
            # Buscar empréstimo antes da alteração
            # ------------------------------------------------

            emprestimo = conexao.execute(
                text("""
                    SELECT
                        e.id,
                        e.livro_id,
                        l.titulo,
                        e.aluno_id,
                        a.nome,
                        a.matricula,
                        e.data_emprestimo,
                        e.status
                    FROM emprestimos e
                    INNER JOIN livros l
                        ON e.livro_id = l.id
                    INNER JOIN alunos a
                        ON e.aluno_id = a.id
                    WHERE e.id = :emprestimo_id
                """),
                {
                    "emprestimo_id": emprestimo_id
                }
            ).fetchone()


            if emprestimo is None:

                raise ValueError(
                    "Empréstimo não encontrado."
                )


            (
                emprestimo_id,
                livro_id,
                livro_titulo,
                aluno_id,
                aluno_nome,
                matricula,
                data_emprestimo,
                status_atual
            ) = emprestimo


            # ------------------------------------------------
            # Verificar status
            # ------------------------------------------------

            if status_atual not in (
                "ATIVO",
                "ATRASADO"
            ):

                raise ValueError(
                    "Este empréstimo não está ativo."
                )


            # ------------------------------------------------
            # Atualizar status
            # ------------------------------------------------

            resultado = conexao.execute(
                text("""
                    UPDATE emprestimos
                    SET status = 'DEVOLVIDO'
                    WHERE id = :emprestimo_id
                    AND status IN ('ATIVO', 'ATRASADO')
                """),
                {
                    "emprestimo_id": emprestimo_id
                }
            )


            if resultado.rowcount == 0:

                raise ValueError(
                    "Empréstimo não encontrado ou já devolvido."
                )


            # ------------------------------------------------
            # Devolver exemplar ao estoque
            # ------------------------------------------------

            conexao.execute(
                text("""
                    UPDATE livros
                    SET quantidade = quantidade + 1
                    WHERE id = :livro_id
                """),
                {
                    "livro_id": livro_id
                }
            )


            # ------------------------------------------------
            # Registrar auditoria
            # ------------------------------------------------

            registrar_auditoria(
                conexao,
                "EMPRESTIMO_DEVOLVIDO",
                "emprestimos",
                emprestimo_id,
                {
                    "aluno_id": aluno_id,
                    "aluno_nome": aluno_nome,
                    "aluno_matricula": matricula,
                    "livro_id": livro_id,
                    "livro_titulo": livro_titulo,
                    "data_emprestimo": data_emprestimo,
                    "status_anterior": status_atual,
                    "status_novo": "DEVOLVIDO"
                }
            )


            # ------------------------------------------------
            # Confirmar
            # ------------------------------------------------

            conexao.commit()


        except Exception:

            conexao.rollback()

            raise