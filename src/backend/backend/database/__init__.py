import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..common.constants import PG_CONNECTION_URL, USE_DB

DOCKER_DATABASE_PATH = "/db/sql_app.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
ACTIVE_DATABASE = SQLALCHEMY_DATABASE_URL

engine = None

if USE_DB == "POSTGRES":
    engine = create_engine(PG_CONNECTION_URL)
elif USE_DB == "SQLITE":
    if os.path.exists(DOCKER_DATABASE_PATH):
        print("Using Docker Database")
        ACTIVE_DATABASE = f"sqlite:///{DOCKER_DATABASE_PATH}"
    else:
        print("Using Local Database")
    print(f"Using database: {ACTIVE_DATABASE}")
    engine = create_engine(ACTIVE_DATABASE, connect_args={"check_same_thread": False})
else:
    raise Exception("No database selected")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
