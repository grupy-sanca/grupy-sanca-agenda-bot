from datetime import datetime
from textwrap import dedent

from grupy_sanca_agenda_bot.events import (
    extract_datetime,
    extract_description,
    extract_event_links,
    extract_location,
    extract_title,
)


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
    assert extract_description(meetup_event_page_soup) == dedent("""\
        O Grupo de Usuários Python de São Carlos (grupy-sanca) organiza o #12 PyLestras, evento com o objetivo de reunir a comunidade, compartilhar conhecimento e divulgar novas tecnologias.
        O evento será composto de 3 palestras, coffee break e um slot para Lightning Talks.
        Lightning Talks são palestras rápidas onde você pode subir no palco e falar sobre o que quiser durante 5 minutos. Os temas não precisam ser relacionados a Python, já tivemos: explicação sobre abelhas, aves, afiação de facas e café. Fique à vontade para falar sobre algo que você goste e ache que possa interessar outras pessoas!
        Cronograma: https://talks.python.org.br/12-pylestras-do-grupy-sanca/schedule
        Nos vemos na Qive (Av. Dr. Carlos Botelho 1869) no dia 07/12 às 13:59!
    """).strip()
