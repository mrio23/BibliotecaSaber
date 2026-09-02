from database.connection import get_connection
from sqlalchemy import text

def contar_livros():
    
    with get_connection() as conexao:
        
        resultado = conexao.execute(
            text("""
                 SELECT COUNT(*)
                 FROM livros
                 """)
        )
    return resultado.scalar_one()

def contar_alunos():
    
    with get_connection() as conexao:
        
        resultado = conexao.execute(
            text("""
                 SELECT COUNT(*)
                 FROM alunos
                 """)
        )
    return resultado.scalar_one()

def contar_emprestimos_ativos():
    
    with get_connection() as conexao:
        
        resultado = conexao.execute(
            text("""
                 SELECT COUNT(*)
                 FROM emprestimos
                 WHERE status = 'ATIVO'
                 """)
        )
        
    return resultado.scalar_one()

def contar_emprestimos_atrasados():
    
    with get_connection() as conexao:
        
        resultado = conexao.execute(
            text("""
                 SELECT COUNT(*)
                 FROM emprestimos
                 WHERE 
                    status = 'ATIVO'
                    AND data_devolucao < CURRENT_DATE
                 """)
        )
        
    return resultado.scalar_one()
