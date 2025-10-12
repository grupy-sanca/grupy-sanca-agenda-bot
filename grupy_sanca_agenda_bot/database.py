from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy import (
    create_engine,
    select,
)
from sqlalchemy.orm import (
    sessionmaker,
)

from grupy_sanca_agenda_bot.models import Base, EventModel
from grupy_sanca_agenda_bot.schemas import Event
from grupy_sanca_agenda_bot.settings import settings

DB_PATH = Path(settings.DB_FILE)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Context-managed session."""
    with SessionLocal() as session:
        yield session


def save_cache(events: List[Event]):
    """Save new events to cache, ignoring duplicates."""
    if not events:
        return

    with SessionLocal() as session:
        existing_ids = set(session.scalars(select(EventModel.identifier)))

        new_events = [event for event in events if event.identifier not in existing_ids]
        if not new_events:
            return

        session.add_all([
            EventModel(**event.model_dump(exclude={"id"}))
            for event in new_events
        ])
        session.commit()


def load_cache() -> List[Event]:
    """Load future events sorted by date."""
    with SessionLocal() as session:
        events = session.scalars(
            select(EventModel)
            .where(EventModel.date_time >= datetime.now())
            .order_by(EventModel.date_time.asc())
        ).all()

        return [
            Event(
                id=event.id,
                identifier=event.identifier,
                title=event.title,
                date_time=event.date_time,
                location=event.location,
                description=event.description,
                link=event.link,
            )
            for event in events
        ]
