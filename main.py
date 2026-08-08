from database.connection import get_connection
from sqlalchemy import text


def cadastrar_livro(titulo, autor, ano_publicacao, quantidade):
    with get_connection() as conexao:
        conexao.execute(
            text("""
                INSERT INTO livros (titulo, autor, ano_publicacao, quantidade)
                VALUES (:titulo, :autor, :ano_publicacao, :quantidade)
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


def registrar_emprestimo(
    livro_id,
    aluno_id,
    data_emprestimo,
    data_devolucao,
    status
):
    with get_connection() as conexao:
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
                "livro_id": livro_id,
                "aluno_id": aluno_id,
                "data_emprestimo": data_emprestimo,
                "data_devolucao": data_devolucao,
                "status": status
            }
        )

        conexao.commit()

# import streamlit as st
# from database.connection import get_connection
# from sqlalchemy import text

# try:
    
#     with get_connection() as conexao:
#         print("Conectado ao Banco de Dados!")
        
# except Exception as erro:
#     print(f"Erro ao conectar com o Banco de Dados: {erro}")
    


# titulo = "O Pequeno Príncipe"
# autor = "Antoine de Saint-Exupéry"
# quantidade = 3

# # dataCadastro = 2026-8-2

# with get_connection() as conexao:
    
#     conexao.execute(text("""
#                          INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo, data_devolucao, status)
#                          VALUES (:livro_id, :aluno_id, :data_emprestimo, :data_devolucao, :status)            
#                          """),
#     {
#         "livro_id": 1,
#         "aluno_id": 1,
#         "data_emprestimo": "2026-08-9",
#         "data_devolucao": "2026-09-1",
#         "status": "DEVOLVIDO"
#     }
#     )
    
#     conexao.commit()
    
#     print("Livro cadastrado.")