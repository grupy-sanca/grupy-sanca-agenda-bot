from datetime import datetime, timedelta

import pytz
import requests
from bs4 import BeautifulSoup

from grupy_sanca_agenda_bot.settings import settings


def get_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the page - status code: {response.status_code}")
        exit(1)


def extract_datetime(event_link):
    html_content = get_html_content(event_link)
    soup = BeautifulSoup(html_content, "html.parser")
    date_time = soup.find("time")["datetime"]
    return datetime.fromisoformat(date_time)


def load_events():
    html_content = get_html_content(settings.MEETUP_GROUP_URL)
    soup = BeautifulSoup(html_content, "html.parser")

    events = []
    for event in soup.select('div[id^="e-"]'):
        title = event.select_one(".ds-font-title-3").get_text(strip=True)
        link = event.find("a", href=True)["href"]
        date_time = extract_datetime(link)
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
