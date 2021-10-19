from datetime import datetime
from fastapi import FastAPI, Response, Depends
from sqlmodel import (
    Field, SQLModel, create_engine, Relationship,
    Column, JSON, Session
)
from typing import Optional, Any, List, Dict


class UserSession(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    events: List["Event"] = Relationship(back_populates="session")


class EventBase(SQLModel):
    category: str
    name: str
    data: Dict[Any, Any] = Field(
        index=False,
        sa_column=Column(JSON)
    )
    timestamp: datetime
    session_id: str = Field(foreign_key="usersession.id")


class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session: Optional[UserSession] = Relationship(back_populates="events")


class EventCreate(EventBase):
    pass


sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/events/", response_class=Response, status_code=204)
async def create_event(
    *, session: Session = Depends(get_session),
    event: EventCreate
):
    event_obj = Event.from_orm(event)
    session.add(event_obj)
    session.commit()
    return
