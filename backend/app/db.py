from sqlmodel import Session, SQLModel, create_engine

from app.models import *

engine = create_engine("sqlite:///data/gaon.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
