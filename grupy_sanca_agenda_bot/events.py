import html
import re
from asyncio import gather
from datetime import datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from httpx import AsyncClient, Timeout

from grupy_sanca_agenda_bot.settings import settings
from grupy_sanca_agenda_bot.utils import load_cache, save_cache


class MeetupExtractor:
    """
    Extractor for Meetup events.

    Uses BeautifulSoup to parse HTML content and extract event details from Meetup.
    """

    def __init__(self, url: str):
        self.url = url

    async def _get_request(self, url):
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    url, timeout=Timeout(settings.TIMEOUT_SECONDS), follow_redirects=True
                )
                if response.status_code == 200:
                    return response.text
                return None
            except Exception:
                return None

    async def get_html_content(self, url):
        content = await self._get_request(url)
        return content

    def extract_event_links(self, soup):
        RX = re.compile(r"^event-card-\d+$")
        event_links = soup.find_all("a", attrs={"data-event-label": RX})
        return [link["href"] for link in event_links]

    def extract_title(self, soup):
        return soup.find("div", attrs={"data-event-label": "top"}).find("h1").get_text(strip=True)

    def extract_datetime(self, soup):
        date_time_element = soup.find("div", attrs={"data-event-label": "info"}).find("time", class_="block")[
            "datetime"
        ]
        return datetime.fromisoformat(date_time_element)

    def extract_location(self, soup):
        try:
            venue_name = soup.find("a", attrs={"data-event-label": "event-location"}).get_text()
            venue_address = soup.find(
                "a", attrs={"data-event-label": "event-location"}
            ).next_sibling.get_text()
            return f"{venue_name} ({venue_address})"
        except Exception:
            return "Evento Online"

    def extract_description(self, soup):
        description_elements = (
            soup.find("div", attrs={"data-event-label": "body"})
            .find("div", class_="break-words")
            .find_all("p")
        )
        return "\n".join([item.get_text() for item in description_elements])

    async def load_events(self):
        events = await load_cache()
        if events:
            return events

        html_content = await self.get_html_content(self.url)
        if html_content is None:
            return events

        soup = BeautifulSoup(html_content, "html.parser")

        event_links = self.extract_event_links(soup)
        event_contents = await gather(*[self.get_html_content(link) for link in event_links])

        for event_content, link in zip(event_contents, event_links):
            inner_soup = BeautifulSoup(event_content, "html.parser")

            events.append(
                {
                    "title": self.extract_title(inner_soup),
                    "date_time": self.extract_datetime(inner_soup),
                    "location": self.extract_location(inner_soup),
                    "description": self.extract_description(inner_soup),
                    "link": link,
                }
            )

        await save_cache(events)
        return events


class OpenEventExtractor:
    """
    Extractor for Open Event Platform events.

    Uses httpx to fetch event data from an Open Event Platform API.
    """

    def __init__(self, url: str):
        self.url = url

    async def _get_request(self, url):
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    url, timeout=Timeout(settings.TIMEOUT_SECONDS), follow_redirects=True
                )
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None

    def extract_datetime(self, timestamp):
        return datetime.fromisoformat(timestamp).astimezone(ZoneInfo("America/Sao_Paulo"))

    def extract_description(self, raw_description):
        soup = BeautifulSoup(raw_description, "html.parser")

        for br in soup.find_all("br"):
            br.replace_with("\n")

        description = soup.get_text()
        description = html.unescape(description)

        return description

    async def load_events(self):
        events = await load_cache()
        if events:
            return events

        resp = await self._get_request(self.url)
        content = resp["data"]

        events = []

        for event in content:
            events.append(
                {
                    "title": event["attributes"]["name"],
                    "date_time": self.extract_datetime(event["attributes"]["starts-at"]),
                    "location": event["attributes"]["location-name"],
                    "description": self.extract_description(event["attributes"]["description"]),
                    "link": "https://eventos.grupysanca.com.br/e/" + event["attributes"]["identifier"],
                }
            )

        await save_cache(events)
        return events
