import streamlit as st
from database.connection import get_connection
from sqlalchemy import text


st.title("Biblioteca Saber")
st.write("Biblioteca virtual para faciliar o monitoramento e acesso dos livros!")

try:
    
    with get_connection() as conexao:
        print("Conectado ao Banco de Dados!")
        
except Exception as erro:
    print(f"Erro ao conectar com o Banco de Dados: {erro}")
    


titulo = "O Pequeno Príncipe"
autor = "Antoine de Saint-Exupéry"
quantidade = 3

# dataCadastro = 2026-8-2

with get_connection() as conexao:
    
    conexao.execute(text("""
                         INSERT INTO emprestimos (livro_id, aluno_id, data_emprestimo, data_devolucao, status)
                         VALUES (:livro_id, :aluno_id, :data_emprestimo, :data_devolucao, :status)            
                         """),
    {
        "livro_id": 1,
        "aluno_id": 1,
        "data_emprestimo": "2026-08-9",
        "data_devolucao": "2026-09-1",
        "status": "DEVOLVIDO"
    }
    )
    
    conexao.commit()
    
    print("Livro cadastrado.")