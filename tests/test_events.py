from datetime import datetime
from textwrap import dedent
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from httpx import Response
from respx.router import MockRouter

from grupy_sanca_agenda_bot.events import MeetupExtractor, OpenEventExtractor
from grupy_sanca_agenda_bot.settings import settings


class TestMeetupExtractor:
    extractor = MeetupExtractor(settings.URL)

    def test_extract_event_links(self, meetup_homepage_soup):
        assert self.extractor.extract_event_links(meetup_homepage_soup) == [
            "https://www.meetup.com/grupysanca/events/304678290/?eventOrigin=group_upcoming_events",
            "https://www.meetup.com/grupysanca/events/304666910/?eventOrigin=group_upcoming_events",
        ]

    def test_extract_title(self, meetup_event_page_soup):
        assert self.extractor.extract_title(meetup_event_page_soup) == "#12 PyLestras do grupy-sanca @ Qive"

    def test_extract_datetime(self, meetup_event_page_soup):
        assert self.extractor.extract_datetime(meetup_event_page_soup) == datetime.fromisoformat(
            "2024-12-07T13:59:00-03:00"
        )

    def test_extract_location(self, meetup_event_page_soup):
        assert (
            self.extractor.extract_location(meetup_event_page_soup)
            == "Qive (Av. Dr. Carlos Botelho, 1869 · São Carlos)"
        )

    def test_extract_description(self, meetup_event_page_soup):
        assert (
            self.extractor.extract_description(meetup_event_page_soup)
            == dedent("""\
            O Grupo de Usuários Python de São Carlos (grupy-sanca) organiza o #12 PyLestras, evento com o objetivo de reunir a comunidade, compartilhar conhecimento e divulgar novas tecnologias.
            O evento será composto de 3 palestras, coffee break e um slot para Lightning Talks.
            Lightning Talks são palestras rápidas onde você pode subir no palco e falar sobre o que quiser durante 5 minutos. Os temas não precisam ser relacionados a Python, já tivemos: explicação sobre abelhas, aves, afiação de facas e café. Fique à vontade para falar sobre algo que você goste e ache que possa interessar outras pessoas!
            Cronograma: https://talks.python.org.br/12-pylestras-do-grupy-sanca/schedule
            Nos vemos na Qive (Av. Dr. Carlos Botelho 1869) no dia 07/12 às 13:59!
        """).strip()  # noqa
        )

    @mock.patch("grupy_sanca_agenda_bot.events.load_cache")
    @mock.patch("grupy_sanca_agenda_bot.events.MeetupExtractor.get_html_content")
    async def test_load_events_with_cache(
        self, mock_get_html_content: mock.AsyncMock, mock_load_cache: mock.AsyncMock
    ):
        mock_load_cache.return_value = [{"some": "data"}]
        await self.extractor.load_events()
        assert mock_get_html_content.call_count == 0

    @pytest.mark.respx(assert_all_mocked=True, assert_all_called=True, using="httpx")
    @mock.patch("grupy_sanca_agenda_bot.events.save_cache")
    @mock.patch("grupy_sanca_agenda_bot.events.load_cache")
    async def test_load_events_without_cache(
        self,
        mock_load_cache: mock.AsyncMock,
        mock_save_cache: mock.AsyncMock,
        respx_mock: MockRouter,
        meetup_homepage_soup,
        meetup_event_page_soup,
    ):
        mock_load_cache.return_value = []
        respx_mock.get(settings.URL).mock(
            return_value=Response(status_code=200, text=str(meetup_homepage_soup))
        )
        respx_mock.get(
            "https://www.meetup.com/grupysanca/events/304678290/?eventOrigin=group_upcoming_events"
        ).mock(return_value=Response(status_code=200, text=str(meetup_event_page_soup)))

        respx_mock.get(
            "https://www.meetup.com/grupysanca/events/304666910/?eventOrigin=group_upcoming_events"
        ).mock(return_value=Response(status_code=200, text=str(meetup_event_page_soup)))

        events = await self.extractor.load_events()
        assert len(events) == 2

        keys = ["title", "date_time", "description", "location", "link"]
        for event in events:
            assert all(key in keys for key in event)
        assert len(respx_mock.calls) == 3

        mock_save_cache.assert_awaited_once_with(events)


class TestOpenEventExtractor:
    extractor = OpenEventExtractor(settings.URL)

    def test_extract_datetime(self):
        assert self.extractor.extract_datetime("2025-09-19T10:00:00+00:00") == datetime(
            2025, 9, 19, 7, 0, tzinfo=ZoneInfo("America/Sao_Paulo")
        )

    def test_extract_description(self):
        raw_description = """<p>Descrição do evento com<br>quebra de linha e &amp; caracteres especiais.</p>"""
        assert self.extractor.extract_description(raw_description) == dedent(
            """\
            Descrição do evento com
            quebra de linha e & caracteres especiais.
        """
        ).strip()

    @mock.patch("grupy_sanca_agenda_bot.events.load_cache")
    @mock.patch("grupy_sanca_agenda_bot.events.OpenEventExtractor._get_request")
    async def test_load_events_with_cache(
        self, mock_get_request: mock.AsyncMock, mock_load_cache: mock.AsyncMock
    ):
        mock_load_cache.return_value = [{"some": "data"}]
        await self.extractor.load_events()
        assert mock_get_request.call_count == 0

    @pytest.mark.respx(assert_all_mocked=True, assert_all_called=True, using="httpx")
    @mock.patch("grupy_sanca_agenda_bot.events.save_cache")
    @mock.patch("grupy_sanca_agenda_bot.events.load_cache")
    async def test_load_events_without_cache(
        self,
        mock_load_cache: mock.AsyncMock,
        mock_save_cache: mock.AsyncMock,
        respx_mock: MockRouter,
        open_event_api_response,
    ):
        mock_load_cache.return_value = []
        respx_mock.get(settings.URL).mock(
            return_value=Response(status_code=200, json=open_event_api_response)
        )

        events = await self.extractor.load_events()
        assert len(events) == 2

        keys = ["title", "date_time", "description", "location", "link"]
        for event in events:
            assert all(key in keys for key in event)
        assert len(respx_mock.calls) == 1

        mock_save_cache.assert_awaited_once_with(events)
