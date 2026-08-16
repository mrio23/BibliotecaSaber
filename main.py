import json

from database.connection import get_connection
from sqlalchemy import text


# ============================================================
# AUDITORIA
# ============================================================

def registrar_auditoria(
    conexao,
    acao,
    entidade,
    entidade_id=None,
    dados=None
):

    conexao.execute(
        text("""
            INSERT INTO auditoria (
                acao,
                entidade,
                entidade_id,
                dados
            )
            VALUES (
                :acao,
                :entidade,
                :entidade_id,
                CAST(:dados AS JSONB)
            )
        """),
        {
            "acao": acao,
            "entidade": entidade,
            "entidade_id": entidade_id,
            "dados": json.dumps(dados or {}, default=str)
        }
    )


def listar_auditoria():

    with get_connection() as conexao:

        resultado = conexao.execute(
            text("""
                SELECT
                    id,
                    acao,
                    entidade,
                    entidade_id,
                    dados,
                    data_hora
                FROM auditoria
                ORDER BY data_hora DESC
            """)
        )

        return resultado.fetchall()


# ============================================================
# LIVROS
# ============================================================

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


# ============================================================
# ALUNOS
# ============================================================

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
                AND status = 'EMPRESTADO'
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

        try:

            # ------------------------------------------------
            # Procurar livro
            # ------------------------------------------------

            livro = conexao.execute(
                text("""
                    SELECT
                        id,
                        titulo
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


            livro_id, livro_titulo = livro


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
                        e.data_emprestimo
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
                data_emprestimo
            ) = emprestimo


            # ------------------------------------------------
            # Atualizar status
            # ------------------------------------------------

            resultado = conexao.execute(
                text("""
                    UPDATE emprestimos
                    SET status = 'DEVOLVIDO'
                    WHERE id = :emprestimo_id
                """),
                {
                    "emprestimo_id": emprestimo_id
                }
            )

            if resultado.rowcount == 0:

                raise ValueError(
                    "Empréstimo não encontrado."
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
                    "status_anterior": "ATIVO",
                    "status_novo": "DEVOLVIDO"
                }
            )


            conexao.commit()

        except Exception:

            conexao.rollback()

            raise

# import json
# from database.connection import get_connection
# from sqlalchemy import text


# # ============================================================
# # LIVROS
# # ============================================================

# def cadastrar_livro(titulo, autor, ano_publicacao, quantidade):
#     with get_connection() as conexao:

#         conexao.execute(
#             text("""
#                 INSERT INTO livros
#                 (
#                     titulo,
#                     autor,
#                     ano_publicacao,
#                     quantidade
#                 )
#                 VALUES
#                 (
#                     :titulo,
#                     :autor,
#                     :ano_publicacao,
#                     :quantidade
#                 )
#             """),
#             {
#                 "titulo": titulo,
#                 "autor": autor,
#                 "ano_publicacao": ano_publicacao,
#                 "quantidade": quantidade
#             }
#         )

#         conexao.commit()


# def listar_livros():
#     with get_connection() as conexao:

#         resultado = conexao.execute(
#             text("""
#                 SELECT *
#                 FROM livros
#                 ORDER BY titulo
#             """)
#         )

#         return resultado.fetchall()

# def listar_alunos():
#     with get_connection() as conexao:
        
#         lista = conexao.execute(text(
#             """
#             SELECT *
#             FROM alunos
#             ORDER BY nome  
#         """)
#     )

#     return lista.fetchall()

# # ============================================================
# # EMPRÉSTIMOS
# # ============================================================

# def registrar_emprestimo(
#     nome_livro,
#     nome_aluno,
#     data_emprestimo,
#     data_devolucao
# ):

#     with get_connection() as conexao:

#         # ----------------------------------------------------
#         # Procurar o livro pelo título
#         # ----------------------------------------------------

#         livro = conexao.execute(
#             text("""
#                 SELECT id
#                 FROM livros
#                 WHERE LOWER(titulo) = LOWER(:titulo)
#             """),
#             {
#                 "titulo": nome_livro
#             }
#         ).fetchone()

#         if livro is None:
#             raise ValueError(
#                 "Livro não encontrado."
#             )

#         # ----------------------------------------------------
#         # Procurar o aluno pelo nome
#         # ----------------------------------------------------

#         aluno = conexao.execute(
#             text("""
#                 SELECT id
#                 FROM alunos
#                 WHERE LOWER(nome) = LOWER(:nome)
#             """),
#             {
#                 "nome": nome_aluno
#             }
#         ).fetchone()

#         if aluno is None:
#             raise ValueError(
#                 "Aluno não encontrado."
#             )

#         # ----------------------------------------------------
#         # Registrar o empréstimo
#         # ----------------------------------------------------

#         conexao.execute(
#             text("""
#                 INSERT INTO emprestimos
#                 (
#                     livro_id,
#                     aluno_id,
#                     data_emprestimo,
#                     data_devolucao,
#                     status
#                 )
#                 VALUES
#                 (
#                     :livro_id,
#                     :aluno_id,
#                     :data_emprestimo,
#                     :data_devolucao,
#                     :status
#                 )
#             """),
#             {
#                 "livro_id": livro.id,
#                 "aluno_id": aluno.id,
#                 "data_emprestimo": data_emprestimo,
#                 "data_devolucao": data_devolucao,
#                 "status": "EMPRESTADO"
#             }
#         )

#         conexao.commit()
        
# def listar_emprestimos():
#     with get_connection() as conexao:
        
#         resultado = conexao.execute(
#             text("""
#                  SELECT
#                     e.id,
#                     l.titulo AS livro,
#                     a.nome AS aluno,
#                     e.data_emprestimo,
#                     e.data_devolucao,
#                     e.status
#                 FROM emprestimos e
#                 INNER JOIN livros l
#                     ON e.livro_id = l.id
#                 INNER JOIN alunos a
#                     ON e.aluno_id = a.id
#                 ORDER BY e.data_emprestimo DESC
#             """)
#         )
        
#         return resultado.fetchall()

# # ----------------------------------------------------
# # Registrar Devolução
# # ----------------------------------------------------
    
# def registrar_devolucao(emprestimo_id):
        
#     with get_connection() as conexao:
            
#         resultado = conexao.execute(
#             text("""
#                  UPDATE emprestimos
#                  SET status = 'DEVOLVIDO'
#                  WHERE id = :emprestimo_id
#                 """),
#                 {
#                    "emprestimo_id": emprestimo_id
#                 }
#             )
            
#         if resultado.rowcount == 0:
#                 raise ValueError(
#                     "Empréstimo não encontrado."
#                 )
                
#         conexao.commit()
        

# def cadastrar_aluno(nome, matricula):
    
#     with get_connection() as conexao:
        
#         conexao.execute(
#             text("""
#                  INSERT INTO alunos
#                  (nome, matricula)
#                  VALUES
#                  (:nome, :matricula)
#                  """),
#             {
#             "nome":nome,
#             "matricula":matricula
#             }
#         )
        
#         conexao.commit()
        
        
# def aluno_possui_emprestimos(aluno_id):
    
#     with get_connection() as conexao:
        
#         resultado = conexao.execute(
#             text("""
#                  SELECT COUNT(*)
#                  FROM emprestimos
#                  WHERE aluno_id = :aluno_id
#                  AND status = 'ATIVO'
#                  """),
#             {
#                 "aluno_id": aluno_id
#             }
#         )        
        
#         quantidade = resultado.scalar_one()
        
#         return int(quantidade) > 0

# def excluir_aluno(aluno_id):

#     with get_connection() as conexao:

#         try:

#             # ====================================================
#             # 1. BUSCAR DADOS DO ALUNO
#             # ====================================================

#             aluno = conexao.execute(
#                 text("""
#                     SELECT id, nome, matricula
#                     FROM alunos
#                     WHERE id = :aluno_id
#                 """),
#                 {
#                     "aluno_id": aluno_id
#                 }
#             ).fetchone()

#             if aluno is None:
#                 raise ValueError(
#                     "Aluno não encontrado no sistema."
#                 )

#             aluno_id, nome, matricula = aluno


#             # ====================================================
#             # 2. BUSCAR EMPRÉSTIMOS DO ALUNO
#             # ====================================================

#             emprestimos = conexao.execute(
#                 text("""
#                     SELECT
#                         e.id,
#                         e.livro_id,
#                         l.titulo,
#                         e.data_emprestimo,
#                         e.data_devolucao,
#                         e.status
#                     FROM emprestimos e
#                     JOIN livros l
#                         ON l.id = e.livro_id
#                     WHERE e.aluno_id = :aluno_id
#                 """),
#                 {
#                     "aluno_id": aluno_id
#                 }
#             ).fetchall()


#             # ====================================================
#             # 3. SALVAR EMPRÉSTIMOS NO HISTÓRICO
#             # ====================================================

#             for emprestimo in emprestimos:

#                 (
#                     emprestimo_id,
#                     livro_id,
#                     livro_titulo,
#                     data_emprestimo,
#                     data_devolucao,
#                     status
#                 ) = emprestimo

#                 conexao.execute(
#                     text("""
#                         INSERT INTO historico_emprestimos (
#                             emprestimo_id,
#                             aluno_id,
#                             aluno_nome,
#                             aluno_matricula,
#                             livro_id,
#                             livro_titulo,
#                             data_emprestimo,
#                             data_devolucao,
#                             status
#                         )
#                         VALUES (
#                             :emprestimo_id,
#                             :aluno_id,
#                             :aluno_nome,
#                             :aluno_matricula,
#                             :livro_id,
#                             :livro_titulo,
#                             :data_emprestimo,
#                             :data_devolucao,
#                             :status
#                         )
#                     """),
#                     {
#                         "emprestimo_id": emprestimo_id,
#                         "aluno_id": aluno_id,
#                         "aluno_nome": nome,
#                         "aluno_matricula": matricula,
#                         "livro_id": livro_id,
#                         "livro_titulo": livro_titulo,
#                         "data_emprestimo": data_emprestimo,
#                         "data_devolucao": data_devolucao,
#                         "status": status
#                     }
#                 )


#             # ====================================================
#             # 4. REGISTRAR EXCLUSÃO NA AUDITORIA
#             # ====================================================

#             conexao.execute(
#                 text("""
#                     INSERT INTO auditoria (
#                         acao,
#                         entidade,
#                         entidade_id,
#                         dados
#                     )
#                     VALUES (
#                         'ALUNO_EXCLUIDO',
#                         'alunos',
#                         :entidade_id,
#                         CAST(:dados AS JSONB)
#                     )
#                 """),
#                 {
#                     "entidade_id": aluno_id,
#                     "dados": json.dumps({
#                         "nome": nome,
#                         "matricula": matricula
#                     })
#                 }
#             )


#             # ====================================================
#             # 5. EXCLUIR EMPRÉSTIMOS OPERACIONAIS
#             # ====================================================

#             conexao.execute(
#                 text("""
#                     DELETE FROM emprestimos
#                     WHERE aluno_id = :aluno_id
#                 """),
#                 {
#                     "aluno_id": aluno_id
#                 }
#             )


#             # ====================================================
#             # 6. EXCLUIR ALUNO
#             # ====================================================

#             resultado = conexao.execute(
#                 text("""
#                     DELETE FROM alunos
#                     WHERE id = :aluno_id
#                 """),
#                 {
#                     "aluno_id": aluno_id
#                 }
#             )

#             if resultado.rowcount == 0:
#                 raise ValueError(
#                     "Aluno não encontrado no sistema."
#                 )


#             # ====================================================
#             # 7. CONFIRMAR TRANSAÇÃO
#             # ====================================================

#             conexao.commit()

#         except Exception:
#             conexao.rollback()
#             raise

# def registrar_auditoria(
#     conexao,
#     acao,
#     entidade,
#     entidade_id=None,
#     dados=None
# ):

#     conexao.execute(
#         text("""
#             INSERT INTO auditoria (
#                 acao,
#                 entidade,
#                 entidade_id,
#                 dados
#             )
#             VALUES (
#                 :acao,
#                 :entidade,
#                 :entidade_id,
#                 CAST(:dados AS JSONB)
#             )
#         """),
#         {
#             "acao": acao,
#             "entidade": entidade,
#             "entidade_id": entidade_id,
#             "dados": json.dumps(dados or {})
#         }
#     )

# def listar_auditoria():
    
#     with get_connection() as conexao:
        
#         resultado = conexao.execute(
#             text("""
#                  SELECT
#                     id,
#                     acao,
#                     entidade,
#                     entidade_id,
#                     dados,
#                     data_hora
#                 FROM auditoria
#                 ORDER BY data_hora DESC   
#                  """)
#         )
        
#         return resultado.fetchall()