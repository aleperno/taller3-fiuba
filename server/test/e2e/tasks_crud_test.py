from src.database import get_session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database import Base

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)

engine = create_engine("postgresql://postgres-test:postgres-test@test_db:5432/postgres")

with engine.connect() as connection:
    connection = connection.execution_options(isolation_level="AUTOCOMMIT")
    connection.execute(text("DROP DATABASE IF EXISTS t3db_test"))
    connection.execute(text("CREATE DATABASE t3db_test"))

def get_test_db():
    engine = create_engine("postgresql://postgres-test:postgres-test@test_db:5432/t3db_test")
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = Session()
    try:
        return session
    finally:
        session.close()

app.dependency_overrides[get_session] = get_test_db

def test_get_all_tasks():
    response = client.get("/tasks/compress")
    assert response.status_code == 200
    assert response.json() == []