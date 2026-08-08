from sqlalchemy import create_engine


engine = create_engine(
        "postgresql+psycopg2://postgres:root@localhost:5432/SaberLibrary"
)

def get_connection():
    return engine.connect()
    