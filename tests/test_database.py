# tests/test_database.py
import os
import tempfile
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import sessionmaker

from grupy_sanca_agenda_bot import database
from grupy_sanca_agenda_bot.database import Base, EventModel, init_db, load_cache, save_cache, update_cache
from grupy_sanca_agenda_bot.schemas import Event


@pytest.fixture()
def temp_db(monkeypatch):
    """Create a temporary SQLite DB and patch the SQLAlchemy engine and session."""
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Patch the main database module to use the temporary DB
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", TestingSessionLocal)

    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal

    os.remove(db_path)


def test_init_db_creates_table(temp_db):
    """Verify that init_db creates the events table."""
    # Recreate DB structure (redundant but tests the function itself)
    init_db()

    # Use ORM to inspect table existence
    insp = inspect(database.engine)
    tables = insp.get_table_names()
    assert "events" in tables


def test_save_cache_inserts_new_events(temp_db):
    session_local = temp_db

    event = Event(
        identifier="identifier",
        title="Test Event",
        date_time=datetime.now(),
        location="Somewhere",
        description="A test description",
        link="http://example.com",
    )

    save_cache([event])

    with session_local() as session:
        results = session.scalars(select(EventModel)).all()

    assert len(results) == 1
    row = results[0]
    assert row.identifier == "identifier"
    assert row.title == "Test Event"
    assert row.location == "Somewhere"
    assert row.description == "A test description"
    assert row.link == "http://example.com"


def test_save_cache_skips_duplicates(temp_db):
    session_local = temp_db

    event = Event(
        identifier="duplicate",
        title="Test Event",
        date_time=datetime.now(),
        location="Somewhere",
        description="A test description",
        link="http://example.com",
    )

    save_cache([event])
    save_cache([event])  # Try to insert duplicate

    with session_local() as session:
        count = session.scalar(
            select(func.count()).select_from(EventModel).where(EventModel.identifier == "duplicate")
        )

    assert count == 1


def test_update_cache_updates_existing_event(temp_db):
    session_local = temp_db

    original = Event(
        identifier="update-me",
        title="Original Title",
        date_time=datetime.now(),
        location="Old Location",
        description="Old description",
        link="http://example.com/old",
    )
    save_cache([original])

    updated = Event(
        identifier="update-me",
        title="Updated Title",
        date_time=datetime.now(),
        location="New Location",
        description="New description",
        link="http://example.com/new",
    )
    update_cache([updated])

    with session_local() as session:
        results = session.scalars(select(EventModel).where(EventModel.identifier == "update-me")).all()

    assert len(results) == 1
    row = results[0]
    assert row.title == "Updated Title"
    assert row.location == "New Location"
    assert row.description == "New description"
    assert row.link == "http://example.com/new"


def test_update_cache_inserts_new_events(temp_db):
    session_local = temp_db

    event = Event(
        identifier="brand-new",
        title="New Event",
        date_time=datetime.now(),
        location="Somewhere",
        description="A description",
        link="http://example.com",
    )
    update_cache([event])

    with session_local() as session:
        results = session.scalars(select(EventModel).where(EventModel.identifier == "brand-new")).all()

    assert len(results) == 1
    assert results[0].title == "New Event"


def test_load_cache_returns_future_events(temp_db):
    now = datetime.now()

    events = [
        Event(
            id=None,
            identifier="past",
            title="Past Event",
            date_time=now - timedelta(days=1),
            location="Old Place",
            description="A description",
            link="link",
        ),
        Event(
            id=None,
            identifier="future1",
            title="Future Event 1",
            date_time=now + timedelta(days=1),
            location="New Place",
            description="A description",
            link="link",
        ),
        Event(
            id=None,
            identifier="future2",
            title="Future Event 2",
            date_time=now + timedelta(days=2),
            location="Newer Place",
            description="A description",
            link="link",
        ),
    ]

    save_cache(events)
    results = load_cache()

    assert len(results) == 2

    identifiers = [event.identifier for event in results]
    assert "past" not in identifiers
    assert "future1" in identifiers
    assert "future2" in identifiers
