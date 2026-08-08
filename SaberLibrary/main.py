from src.connection import get_connection
from sqlalchemy import text


try:
    
    with get_connection() as conexao:
        print("Conectado ao Banco de Dados!")
        
except Exception as erro:
    print(f"Erro ao conectar com o Banco de Dados: {erro}")
    


nomeLivro = "O Pequeno Príncipe"
autor = "Antoine de Saint-Exupéry"
dataCadastro = 2026-8-4
isbn = "978-8595081512"
# dataCadastro = 2026-8-2

with get_connection() as conexao:
    
    conexao.execute(text("""                      
                         """),
    {
        "nomeLivro":nomeLivro,
        "autor": autor,
        "isbn": isbn
    }
    )
    
    conexao.commit()
    
    print("Livro cadastrado.")

conexao.close