import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@st.cache_resource(show_spinner=False)
def _criar_engine(database_url: str) -> Engine:
    """Cria e reutiliza o engine do SQLAlchemy durante a execução do app."""
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


def get_engine() -> Engine:
    """Retorna o engine configurado a partir dos Secrets do Streamlit."""
    try:
        database_url = st.secrets["DATABASE_URL"]
    except KeyError as exc:
        raise RuntimeError(
            "DATABASE_URL não foi configurada nos Secrets do Streamlit."
        ) from exc

    if not database_url or not str(database_url).strip():
        raise RuntimeError(
            "DATABASE_URL está vazia nos Secrets do Streamlit."
        )

    return _criar_engine(str(database_url).strip())


def get_connection():
    """Abre uma conexão curta com o banco de dados.

    O chamador continua responsável por commit/rollback das transações
    quando executar operações de escrita.
    """
    return get_engine().connect()
