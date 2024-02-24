from sqlalchemy.orm import Session
from backend.database import models


def get_create_user_by_email(db: Session, email: str, name:str):
    db_user = db.query(models.User).filter(models.User.email == email).one_or_none()
    if db_user is None:
        print(f"Creando usuario con email {email}")
        db_user = models.User(email=email, name=name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        print(f"Usuario con email {email} ya existe")
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).one_or_none()
