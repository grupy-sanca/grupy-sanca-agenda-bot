import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from unittest import mock

import pytest

from grupy_sanca_agenda_bot.database import delete_cache, init_db, load_cache, save_cache


@pytest.fixture()
def temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    with mock.patch("grupy_sanca_agenda_bot.database.settings") as mock_settings:
        mock_settings.DB_FILE = db_path
        init_db()
        yield db_path

    os.remove(db_path)


def test_init_db_creates_table(temp_db):
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        assert cursor.fetchone() is not None


def test_save_cache_inserts_new_events(temp_db):
    events = [
        {
            "identifier": "identifier",
            "title": "Test Event",
            "date_time": datetime.now(),
            "location": "Somewhere",
            "description": "A test description",
            "link": "http://example.com",
        }
    ]

    save_cache(events)

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT identifier, title, location, description, link FROM events")
        rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "identifier"
    assert rows[0][1] == "Test Event"
    assert rows[0][2] == "Somewhere"
    assert rows[0][3] == "A test description"
    assert rows[0][4] == "http://example.com"


def test_save_cache_skips_duplicates(temp_db):
    event = {
        "identifier": "duplicate",
        "title": "Test Event",
        "date_time": datetime.now(),
        "location": "Somewhere",
        "description": "A test description",
        "link": "http://example.com",
    }

    save_cache([event])
    save_cache([event])  # Try to insert duplicate

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM events WHERE identifier='duplicate'")
        count = cursor.fetchone()[0]

    assert count == 1


def test_load_cache_returns_future_events(temp_db):
    now = datetime.now()

    events = [
        {
            "identifier": "past",
            "title": "Past Event",
            "date_time": now - timedelta(days=1),
            "location": "Old Place",
            "description": "A description",
            "link": "link",
        },
        {
            "identifier": "future1",
            "title": "Future Event 1",
            "date_time": now + timedelta(days=1),
            "location": "New Place",
            "description": "A description",
            "link": "link",
        },
        {
            "identifier": "future2",
            "title": "Future Event 2",
            "date_time": now + timedelta(days=2),
            "location": "Newer Place",
            "description": "A description",
            "link": "link",
        },
    ]

    save_cache(events)
    results = load_cache()
    assert len(results) == 2

    identifiers = [event["identifier"] for event in results]
    assert "past" not in identifiers
    assert "future1" in identifiers
    assert "future2" in identifiers


def test_delete_cache_removes_all_rows(temp_db):
    event = {
        "identifier": "delete",
        "title": "Delete Me",
        "date_time": datetime.now(),
        "location": "Somewhere",
        "description": "A description",
        "link": "http://example.com",
    }

    save_cache([event])
    delete_cache()

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]

    assert count == 0
