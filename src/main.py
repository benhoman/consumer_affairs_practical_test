from fastapi import FastAPI
from sqlmodel import Field, SQLModel, create_engine
from typing import Optional

app = FastAPI()


class UserSession(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)


sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
