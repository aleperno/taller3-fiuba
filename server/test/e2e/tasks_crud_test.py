from src.database import get_session
from src.database import Base
from src.app import app

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from celery import Celery

from fastapi.testclient import TestClient



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

def get_celery():
    celery = Celery()
    celery.config_from_object('e2e_celery_config')
    

app.dependency_overrides[get_session] = get_test_db
app.dependency_overrides[get_celery] = get_celery

def test_create_tasks_and_get_all():
    create_task_request = {
        "global_palette_opt": True,
        "white_background": True,
        "colours": 5,
        "total_pages": 2,
        "selected_pages": [0,1]
    }
    post_response = client.post("/tasks/compress", json=create_task_request)

    response = client.get("/tasks/compress")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": post_response.json()["id"],
            "global_palette_opt": True,
            "white_background": True,
            "colours": 5,
            "total_pages": 2,
            "selected_pages": [0,1],
            "status": "pending",
            "pages_done": 0
        }
    ]