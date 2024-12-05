from bs4 import BeautifulSoup
from pytest import fixture


@fixture
def meetup_homepage_soup():
    with open("tests/fixtures/meetup_homepage_example.html") as f:
        return BeautifulSoup(f.read(), "html.parser")


@fixture
def meetup_event_page_soup():
    with open("tests/fixtures/meetup_event_page_example.html") as f:
        return BeautifulSoup(f.read(), "html.parser")
