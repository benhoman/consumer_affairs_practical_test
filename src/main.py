from datetime import datetime
from fastapi import FastAPI, Response, Depends, Query, BackgroundTasks
from pydantic import validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import (
    Field, SQLModel, create_engine, Relationship,
    Column, JSON, Session, select
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

    @validator('timestamp')
    def timestamp_must_not_be_in_future(cls, v):
        if v > datetime.utcnow():
            raise ValueError('timestamp is in the future')
        return v

    @validator('data')
    def payload_validation(cls, v, values, **kwargs):
        # Implement category + name specific validation
        category = values.get('category')
        name = values.get('name')

        if category == "page interaction" and name == "pageview":
            expected_keys = ["host", "path"]
            if not all(key in v for key in expected_keys):
                raise ValueError('payload missing data')
        elif category == "page interaction" and name == "cta click":
            expected_keys = ["host", "path", "element"]
            if not all(key in v for key in expected_keys):
                raise ValueError('payload missing data')
        elif category == "form interaction" and name == "submit":
            expected_keys = ["host", "path", "form"]
            if not all(key in v for key in expected_keys):
                raise ValueError('payload missing data')
            elif not isinstance(v.get("form"), dict):
                raise ValueError('payload form object is bad')

        return v


class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session: Optional[UserSession] = Relationship(back_populates="events")


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int


sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


def create_event_in_background(session: Session, event: EventCreate):
    try:
        user_session_obj = UserSession(id=event.session_id)
        session.add(user_session_obj)
        session.commit()
    except IntegrityError:
        session.rollback()

    event_obj = Event.from_orm(event)
    session.add(event_obj)
    session.commit()



@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/events/", response_class=Response, status_code=204)
def create_event(
    *, session: Session = Depends(get_session),
    background_tasks: BackgroundTasks, event: EventCreate
):
    background_tasks.add_task(
        create_event_in_background,
        session=session, event=event
    )
    return


@app.get("/events/session/{session_id}", response_model=List[EventRead])
def get_events_by_session_id(
    *, session: Session = Depends(get_session), session_id: str,
    offset: int = 0, limit: int = Query(default=100, lte=100)
):
    events = session.exec(
        select(Event).where(
            Event.session_id == session_id
        ).offset(offset).limit(limit)).all()
    return events


@app.get("/events/category/{category_name}", response_model=List[EventRead])
def get_events_by_category(
    *, session: Session = Depends(get_session), category_name: str,
    offset: int = 0, limit: int = Query(default=100, lte=100)
):
    events = session.exec(
        select(Event).where(
            Event.category == category_name
        ).offset(offset).limit(limit)).all()
    return events
