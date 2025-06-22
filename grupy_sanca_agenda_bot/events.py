import re
from asyncio import gather
from datetime import datetime, timedelta

import pytz
from bs4 import BeautifulSoup
from httpx import AsyncClient, Timeout

from grupy_sanca_agenda_bot.settings import settings
from grupy_sanca_agenda_bot.utils import load_cache, save_cache


async def _get_request(url):
    async with AsyncClient() as client:
        try:
            response = await client.get(url, timeout=Timeout(settings.TIMEOUT_SECONDS), follow_redirects=True)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None


async def get_html_content(url):
    content = await _get_request(url)
    return content


def extract_event_links(soup):
    RX = re.compile(r"^event-card-\d+$")
    event_links = soup.find_all("a", attrs={"data-event-label": RX})
    return [link["href"] for link in event_links]


def extract_title(soup):
    return soup.find("div", attrs={"data-event-label": "top"}).find("h1").get_text(strip=True)


def extract_datetime(soup):
    date_time_element = soup.find("div", attrs={"data-event-label": "info"}).find("time", class_="block")[
        "datetime"
    ]
    return datetime.fromisoformat(date_time_element)


def extract_location(soup):
    venue_name = soup.find("a", attrs={"data-event-label": "event-location"}).get_text()
    venue_address = soup.find("a", attrs={"data-event-label": "event-location"}).next_sibling.get_text()
    return f"{venue_name} ({venue_address})"


def extract_description(soup):
    description_elements = (
        soup.find("div", attrs={"data-event-label": "body"}).find("div", class_="break-words").find_all("p")
    )
    return "\n".join([item.get_text() for item in description_elements])


async def load_events():
    events = await load_cache()
    if events:
        return events

    html_content = await get_html_content(settings.MEETUP_GROUP_URL)
    if html_content is None:
        return events

    soup = BeautifulSoup(html_content, "html.parser")

    event_links = extract_event_links(soup)
    event_contents = await gather(*[get_html_content(link) for link in event_links])

    for event_content, link in zip(event_contents, event_links):
        inner_soup = BeautifulSoup(event_content, "html.parser")

        events.append(
            {
                "title": extract_title(inner_soup),
                "date_time": extract_datetime(inner_soup),
                "location": extract_location(inner_soup),
                "description": extract_description(inner_soup),
                "link": link,
            }
        )

    await save_cache(events)

    return events


def filter_events(events, period="agenda"):
    tz = pytz.timezone("America/Sao_Paulo")

    today = datetime.now(tz)
    if period == "mensal":
        start = today.replace(day=1, hour=0, minute=0, second=0)
        end = (start + timedelta(days=31)).replace(day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
    elif period == "semanal":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == "hoje":
        start = today.replace(hour=0, minute=0, second=0)
        end = today.replace(hour=23, minute=59, second=59)
    elif period == "agenda":
        start = today
        end = today + timedelta(days=365)

    return [event for event in events if start <= event["date_time"].astimezone(tz) <= end]


def slice_events(events, quantity):
    return events[:quantity]


def format_event_message(events, header="", description=True):
    message = f"*📅 {header}:*\n\n"
    for event in events:
        message += f"*{event['title']}*\n\n"
        message += f"*🕒 Data e Hora:* {event['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        message += f"*📍 Local:* {event['location']}\n\n"
        if description:
            message += f"*📝 Descrição:*\n{event['description']}\n\n"
        message += f"🔗 [Clique aqui para se inscrever no Meetup]({event['link']})\n\n"
    return message
