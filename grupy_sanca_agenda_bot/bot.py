from telegram import Update
from telegram.ext import Application

from grupy_sanca_agenda_bot.events import format_event_message
from grupy_sanca_agenda_bot.settings import settings


async def send_message(message: str, application: Application) -> None:
    await application.bot.send_message(
        chat_id=settings.GROUP_CHAT_ID,
        text=message,
        parse_mode="Markdown",
    )


async def reply_message(message: str, update: Update) -> None:
    await update.message.reply_text(message, parse_mode="Markdown")


async def send_events(events, application, header="", description=True):
    if events:
        message = f"*📅 {header}:*\n\n"
        for event in events:
            message += format_event_message(event, description)
        await send_message(message, application)
    else:
        await send_message(f"❌ Não há {header} agendados.", application)
