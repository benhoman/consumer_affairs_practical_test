from datetime import datetime
from fastapi import FastAPI
from sqlmodel import Field, SQLModel, create_engine, Relationship, Column, JSON
from typing import Optional, Any


class UserSession(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)


class EventBase(SQLModel):
    category: str
    name: str
    data: dict[Any, Any] = Field(
        index=False,
        sa_column=Column(JSON)
    )
    timestamp: datetime
    session_id: Optional[str] = Field(
        default=None,
        foreign_key="usersession.id"
    )


class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session: Optional[UserSession] = Relationship(back_populates="events")


sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url)


app = FastAPI()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
