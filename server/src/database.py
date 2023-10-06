import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

PG_USER = os.environ.get('POSTGRES_USER', 't3user')
PG_PASS = os.environ.get('POSTGRES_PASSWORD', 't3pass')
PG_DB = os.environ.get('POSTGRES_DB', 't3db')
PG_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
PG_PORT = os.environ.get('POSTGRES_PORT', '5432')
PG_CONNECTION_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"


engine = create_engine(PG_CONNECTION_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)

def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
