from datetime import datetime
from textwrap import dedent
from unittest import mock

from httpx import Response
from respx.router import MockRouter

from grupy_sanca_agenda_bot.events import (
    extract_datetime,
    extract_description,
    extract_event_links,
    extract_location,
    extract_title,
    load_events,
)
from grupy_sanca_agenda_bot.settings import settings


def test_extract_event_links(meetup_homepage_soup):
    assert extract_event_links(meetup_homepage_soup) == [
        "https://www.meetup.com/grupysanca/events/304678290/?eventOrigin=group_upcoming_events",
        "https://www.meetup.com/grupysanca/events/304666910/?eventOrigin=group_upcoming_events",
    ]


def test_extract_title(meetup_event_page_soup):
    assert extract_title(meetup_event_page_soup) == "#12 PyLestras do grupy-sanca @ Qive"


def test_extract_datetime(meetup_event_page_soup):
    assert extract_datetime(meetup_event_page_soup) == datetime.fromisoformat("2024-12-07T13:59:00-03:00")


def test_extract_location(meetup_event_page_soup):
    assert extract_location(meetup_event_page_soup) == "Qive (Av. Dr. Carlos Botelho, 1869 · São Carlos)"


def test_extract_description(meetup_event_page_soup):
    assert (
        extract_description(meetup_event_page_soup)
        == dedent("""\
        O Grupo de Usuários Python de São Carlos (grupy-sanca) organiza o #12 PyLestras, evento com o objetivo de reunir a comunidade, compartilhar conhecimento e divulgar novas tecnologias.
        O evento será composto de 3 palestras, coffee break e um slot para Lightning Talks.
        Lightning Talks são palestras rápidas onde você pode subir no palco e falar sobre o que quiser durante 5 minutos. Os temas não precisam ser relacionados a Python, já tivemos: explicação sobre abelhas, aves, afiação de facas e café. Fique à vontade para falar sobre algo que você goste e ache que possa interessar outras pessoas!
        Cronograma: https://talks.python.org.br/12-pylestras-do-grupy-sanca/schedule
        Nos vemos na Qive (Av. Dr. Carlos Botelho 1869) no dia 07/12 às 13:59!
    """).strip()  # noqa
    )


@mock.patch("grupy_sanca_agenda_bot.events.load_cache")
@mock.patch("grupy_sanca_agenda_bot.events.get_html_content")
async def test_load_events_with_cache(mock_get_html_content: mock.AsyncMock, mock_load_cache: mock.AsyncMock):
    mock_load_cache.return_value = [{"some": "data"}]
    await load_events()
    assert mock_get_html_content.call_count == 0


@mock.patch("grupy_sanca_agenda_bot.events.save_cache")
@mock.patch("grupy_sanca_agenda_bot.events.load_cache")
async def test_load_events_without_cache(
    mock_load_cache: mock.AsyncMock,
    mock_save_cache: mock.AsyncMock,
    respx_mock: MockRouter,
    meetup_homepage_soup,
    meetup_event_page_soup,
):
    mock_load_cache.return_value = []
    respx_mock.get(settings.MEETUP_GROUP_URL).mock(
        return_value=Response(status_code=200, text=str(meetup_homepage_soup))
    )
    respx_mock.get(
        "https://www.meetup.com/grupysanca/events/304678290/?eventOrigin=group_upcoming_events"
    ).mock(return_value=Response(status_code=200, text=str(meetup_event_page_soup)))

    respx_mock.get(
        "https://www.meetup.com/grupysanca/events/304666910/?eventOrigin=group_upcoming_events"
    ).mock(return_value=Response(status_code=200, text=str(meetup_event_page_soup)))
    events = await load_events()
    assert len(events) == 2
    keys = ["title", "date_time", "description", "location", "link"]
    for i in range(len(events)):
        assert all(key in keys for key in events[i])
    assert len(respx_mock.calls) == 3
    mock_save_cache.assert_awaited_once_with(events)
