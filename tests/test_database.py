# tests/test_database.py
import os
import tempfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

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


def test_update_cache_handles_timezone_aware_datetime(temp_db):
    session_local = temp_db

    event_utc = Event(
        identifier="utc-event",
        title="UTC Event",
        date_time=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        location="UTC Location",
        description="UTC description",
        link="http://example.com/utc",
    )
    update_cache([event_utc])

    with session_local() as session:
        results = session.scalars(select(EventModel).where(EventModel.identifier == "utc-event")).all()

    assert len(results) == 1
    assert results[0].date_time == datetime(2025, 1, 15, 12, 0, 0)


def test_update_cache_converts_timezone_to_utc(temp_db):
    session_local = temp_db

    event_sao_paulo = Event(
        identifier="sao-paulo-event",
        title="Sao Paulo Event",
        date_time=datetime(2025, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo")),
        location="Sao Paulo",
        description="Sao Paulo description",
        link="http://example.com/sp",
    )
    update_cache([event_sao_paulo])

    with session_local() as session:
        results = session.scalars(select(EventModel).where(EventModel.identifier == "sao-paulo-event")).all()

    assert len(results) == 1
    expected_utc = datetime(2025, 1, 15, 15, 0, 0)
    assert results[0].date_time == expected_utc


def test_load_cache_returns_utc_timezone(temp_db):
    now = datetime.now(timezone.utc)

    event = Event(
        id=None,
        identifier="future-utc",
        title="Future UTC Event",
        date_time=now + timedelta(days=1),
        location="UTC Place",
        description="A description",
        link="link",
    )
    save_cache([event])
    results = load_cache()

    assert len(results) == 1
    assert results[0].date_time.tzinfo == timezone.utc


def test_update_and_load_roundtrip_with_timezone(temp_db):
    event_ny = Event(
        identifier="ny-event",
        title="New York Event",
        date_time=datetime(2027, 6, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York")),
        location="New York",
        description="NY description",
        link="http://example.com/ny",
    )
    update_cache([event_ny])

    results = load_cache()

    assert len(results) == 1
    assert results[0].identifier == "ny-event"
    assert results[0].date_time.tzinfo == timezone.utc
    assert results[0].date_time == event_ny.date_time.astimezone(timezone.utc)


def test_get_session_yields_session(temp_db):
    session_gen = database.get_session()
    session = next(session_gen)
    assert session is not None
    assert hasattr(session, "execute")
    assert hasattr(session, "commit")


def test_save_cache_empty_list(temp_db):
    save_cache([])
    with temp_db() as session:
        count = session.scalar(select(func.count()).select_from(EventModel))
    assert count == 0


def test_update_cache_empty_list(temp_db):
    update_cache([])
    with temp_db() as session:
        count = session.scalar(select(func.count()).select_from(EventModel))
    assert count == 0


def test_load_cache_empty_database(temp_db):
    results = load_cache()
    assert results == []


def test_save_cache_with_timezone_aware_datetime(temp_db):
    event = Event(
        identifier="tz-aware",
        title="TZ Aware Event",
        date_time=datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        location="UTC Location",
        description="UTC description",
        link="http://example.com/tz",
    )
    save_cache([event])

    with temp_db() as session:
        results = session.scalars(select(EventModel).where(EventModel.identifier == "tz-aware")).all()

    assert len(results) == 1
    assert results[0].date_time == datetime(2025, 1, 15, 12, 0, 0)
