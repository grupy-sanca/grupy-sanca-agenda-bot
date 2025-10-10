import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from grupy_sanca_agenda_bot.settings import settings


def init_db():
    with sqlite3.connect(settings.DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier STRING UNIQUE,
                title TEXT,
                date_time TEXT,
                location TEXT,
                description TEXT,
                link TEXT
            )
        """)
        conn.commit()


def save_cache(events: List[Dict[str, Any]]):
    with sqlite3.connect(settings.DB_FILE) as conn:
        existing_ids = {row[0] for row in conn.execute("SELECT identifier FROM events").fetchall()}
        events = [e for e in events if e["identifier"] not in existing_ids]
        if not events:
            return

        conn.executemany(
            """
            INSERT INTO events (identifier, title, date_time, location, description, link)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            [
                (
                    e["identifier"],
                    e["title"],
                    e["date_time"].isoformat() if isinstance(e["date_time"], datetime) else e["date_time"],
                    e["location"],
                    e["description"],
                    e["link"],
                )
                for e in events
            ],
        )
        conn.commit()


def load_cache() -> List[Dict[str, Any]]:
    with sqlite3.connect(settings.DB_FILE) as conn:
        cursor = conn.execute(
            """
            SELECT identifier, title, date_time, location, description, link
            FROM events
            WHERE date_time >= ?
            ORDER BY date_time ASC
        """,
            (datetime.now().isoformat(),),
        )

        rows = cursor.fetchall()
        return [
            {
                "identifier": row[0],
                "title": row[1],
                "date_time": datetime.fromisoformat(row[2]),
                "location": row[3],
                "description": row[4],
                "link": row[5],
            }
            for row in rows
        ]


def delete_cache():
    with sqlite3.connect(settings.DB_FILE) as conn:
        conn.execute("DELETE FROM events")
        conn.commit()
