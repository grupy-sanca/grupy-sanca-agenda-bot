from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application

from grupy_sanca_agenda_bot.constants import PeriodEnum
from grupy_sanca_agenda_bot.schemas import Event
from grupy_sanca_agenda_bot.settings import settings


def check_is_period_valid(value: str) -> bool:
    return value in PeriodEnum._value2member_map_


async def send_message(message: str, application: Application) -> None:
    await application.bot.send_message(
        chat_id=settings.GROUP_CHAT_ID,
        message_thread_id=settings.GROUP_CHAT_TOPIC_ID,
        text=message,
        parse_mode="Markdown",
    )


async def reply_message(message: str, update: Update) -> None:
    await update.message.reply_text(message, parse_mode="Markdown")


def filter_events(events: Event, period=PeriodEnum.agenda):
    now = datetime.now(ZoneInfo(settings.TIMEZONE))
    if period == PeriodEnum.mensal:
        start = now.replace(day=1, hour=0, minute=0, second=0)
        end = (start + timedelta(days=31)).replace(day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
    elif period == PeriodEnum.semanal:
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)
    elif period == PeriodEnum.hoje:
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
    elif period == PeriodEnum.agenda:
        start = now
        end = now + timedelta(days=365)

    return [event for event in events if start <= event.date_time <= end]


def slice_events(events, quantity):
    return events[:quantity]


def format_event_message(events: Event, header="", description=True):
    message = f"*📅 {header}:*\n\n"
    for event in events:
        date_time = event.date_time.astimezone(ZoneInfo(settings.TIMEZONE)).strftime("%d/%m/%Y às %Hh%M")
        message += f"*{event.title}*\n\n"
        message += f"*🕒 Data e Hora:* {date_time}\n"
        message += f"*📍 Local:* {event.location}\n\n"
        if description:
            message += f"*📝 Descrição:*\n{event.description}\n\n"
        message += f"🔗 [Clique aqui para se inscrever no evento]({event.link})\n\n"
    return message
