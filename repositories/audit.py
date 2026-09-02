import json

from database.connection import get_connection
from sqlalchemy import text

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
