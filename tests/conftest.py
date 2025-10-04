from datetime import datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from pytest import fixture


@fixture
def meetup_homepage_soup():
    with open("tests/fixtures/meetup_homepage_example.html") as f:
        return BeautifulSoup(f, "html.parser")


@fixture
def meetup_event_page_soup():
    with open("tests/fixtures/meetup_event_page_example.html") as f:
        return BeautifulSoup(f, "html.parser")


@fixture
def open_event_api_response():
    return {
        "data": [
            {
                "type": "event",
                "relationships": {},
                "id": "123456",
                "attributes": {
                    "name": "Sample Event",
                    "starts-at": "2024-07-01T10:00:00+00:00",
                    "location-name": "Sample Location",
                    "description": "This is a sample event description.",
                    "url": "https://example.com/events/123456",  # Example URL
                    "identifier": "sample-event-123456",
                },
                "links": {"self": "https://api.example.com/events/123456"},
            },
            {
                "type": "event",
                "relationships": {},
                "id": "789012",
                "attributes": {
                    "name": "Another Event",
                    "starts-at": "2024-07-15T15:00:00+00:00",
                    "location-name": None,
                    "description": "This is another event description.",
                    "url": "https://example.com/events/789012",  # Example URL
                    "identifier": "another-event-789012",
                },
                "links": {"self": "https://api.example.com/events/789012"},
            },
        ]
    }


@fixture
def open_event_api_response_unsorted():
    return {
        "data": [
            {
                "type": "event",
                "relationships": {},
                "id": "123456",
                "attributes": {
                    "name": "Sample Event",
                    "starts-at": "2024-07-15T10:00:00+00:00",
                    "location-name": "Sample Location",
                    "description": "This is a sample event description.",
                    "url": "https://example.com/events/123456",  # Example URL
                    "identifier": "sample-event-123456",
                },
                "links": {"self": "https://api.example.com/events/123456"},
            },
            {
                "type": "event",
                "relationships": {},
                "id": "789012",
                "attributes": {
                    "name": "Another Event",
                    "starts-at": "2024-07-14T09:00+00:00",
                    "location-name": None,
                    "description": "This is another event description.",
                    "url": "https://example.com/events/789012",  # Example URL
                    "identifier": "another-event-789012",
                },
                "links": {"self": "https://api.example.com/events/789012"},
            },
        ]
    }


@fixture
def events():
    return [
        {
            "title": "Event 1",
            "date_time": datetime(2024, 7, 10, 20, 0, 0).astimezone(ZoneInfo("America/Sao_Paulo")),
            "location": "Location 1",
            "description": "Description 1",
            "link": "https://example.com/events/1",
        },
        {
            "title": "Event 2",
            "date_time": datetime(2024, 7, 15, 15, 0, 0).astimezone(ZoneInfo("America/Sao_Paulo")),
            "location": "Location 2",
            "description": "Description 2",
            "link": "https://example.com/events/2",
        },
        {
            "title": "Event 3",
            "date_time": datetime(2024, 7, 20, 18, 0, 0).astimezone(ZoneInfo("America/Sao_Paulo")),
            "location": "Location 3",
            "description": "Description 3",
            "link": "https://example.com/events/3",
        },
        {
            "title": "Event 4",
            "date_time": datetime(2024, 8, 5, 19, 0, 0).astimezone(ZoneInfo("America/Sao_Paulo")),
            "location": "Location 4",
            "description": "Description 4",
            "link": "https://example.com/events/4",
        },
    ]
