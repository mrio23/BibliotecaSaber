import streamlit as st
from sqlalchemy import create_engine

DATABASE_URL = st.secrets["DATABASE_URL"]

# Reuse a small pool of database connections across Streamlit reruns.
# The conservative pool size helps avoid exhausting Neon connection limits.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_timeout=10,
    pool_recycle=1800,
    connect_args={"connect_timeout": 10},
)


def get_connection():
    """Return a connection checked out from SQLAlchemy's reusable pool."""
    return engine.connect()
