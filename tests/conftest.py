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
