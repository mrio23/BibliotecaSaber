import streamlit as st
from sqlalchemy import create_engine

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
    )

def get_connection():
    return engine.connect()