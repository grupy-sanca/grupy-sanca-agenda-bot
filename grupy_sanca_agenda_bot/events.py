from asyncio import sleep
from datetime import datetime, timedelta

import pytz
from bs4 import BeautifulSoup
from httpx import AsyncClient

from grupy_sanca_agenda_bot.settings import settings


async def _get_request(url):
    async with AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None


async def get_html_content(url):
    content = await _get_request(url)
    if content is None:
        await sleep(0.5)
        content = await _get_request(url)
    return content


async def extract_datetime(event_link):
    html_content = await get_html_content(event_link)
    if html_content is None:
        return None
    soup = BeautifulSoup(html_content, "html.parser")
    date_time = soup.find("time")["datetime"]
    return datetime.fromisoformat(date_time)


async def load_events():
    events = []
    html_content = await get_html_content(settings.MEETUP_GROUP_URL)
    if html_content is None:
        return events
    soup = BeautifulSoup(html_content, "html.parser")

    for event in soup.select('div[id^="e-"]'):
        title = event.select_one(".ds-font-title-3").get_text(strip=True)
        link = event.find("a", href=True)["href"]
        date_time = await extract_datetime(link)
        if date_time is None:
            continue
        location = event.select_one(".text-gray6").get_text(strip=True)
        description = (
            "\n".join(
                p.get_text(strip=True)
                for p in event.select(".utils_cardDescription__1Qr0x p")
            )
            if event.select_one(".utils_cardDescription__1Qr0x")
            else None
        )

        events.append(
            {
                "title": title,
                "date_time": date_time,
                "location": location,
                "description": description,
                "link": link,
            }
        )

    return events


def filter_events(events, period="week"):
    tz = pytz.timezone("America/Sao_Paulo")

    today = datetime.now(tz)
    if period == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == "agenda":
        start = today
        end = today + timedelta(days=365)
    elif period == "today":
        start = today.replace(hour=0, minute=0, second=0)
        end = today.replace(hour=23, minute=59, second=59)

    return [
        event for event in events if start <= event["date_time"].astimezone(tz) <= end
    ]


def format_event_message(events, header="", description=True):
    message = f"*📅 {header}:*\n\n"
    for event in events:
        message += f"*{event['title']}*\n\n"
        message += (
            f"*🕒 Data e Hora:* {event['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        )
        message += f"*📍 Local:* {event['location']}\n\n"
        if description:
            message += f"*📝 Descrição:*\n{event['description']}\n\n"
        message += f"🔗 [Clique aqui para se inscrever no Meetup]({event['link']})\n\n"
    return message
