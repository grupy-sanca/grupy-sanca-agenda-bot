import pickle
from enum import StrEnum, auto
from pathlib import Path

from telegram import Update
from telegram.ext import Application

from grupy_sanca_agenda_bot.settings import settings


class PeriodEnum(StrEnum):
    mensal = auto()
    semanal = auto()
    hoje = auto()
    agenda = auto()


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


async def delete_cache():
    try:
        Path.unlink(Path("events"))
    except Exception:
        pass


async def load_cache():
    events = []
    try:
        with open("events", "rb") as fp:
            events = pickle.load(fp)
    except Exception:
        return events
    return events


async def save_cache(events):
    try:
        with open("events", "wb") as fp:
            pickle.dump(events, fp)
    except Exception:
        pass
