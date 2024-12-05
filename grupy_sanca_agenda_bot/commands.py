from telegram import Update
from telegram.ext import ContextTypes

from grupy_sanca_agenda_bot.events import (
    filter_events,
    format_event_message,
    load_events,
)
from grupy_sanca_agenda_bot.settings import settings
from grupy_sanca_agenda_bot.utils import delete_cache, reply_message


async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events = await load_events()

    if events:
        event = events[0]
        message = format_event_message([event], header="Próximo Evento", description=True)
        await reply_message(message, update)
    else:
        await reply_message("Sem próximos eventos", update)


async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events = filter_events(await load_events(), period="agenda")

    if events:
        message = format_event_message(events, header="Agenda", description=False)
        await reply_message(message, update)
    else:
        await reply_message("Sem próximos eventos", update)


async def force_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if settings.ADMINS and update.message.from_user.id in settings.ADMINS:
        await delete_cache()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 *Fique por dentro de todos os eventos do grupy-sanca!* 🤖\n\n"
        "Comandos:\n"
        "⚙️ /proximo: mostra o próximo evento\n"
        "⚙️ /agenda: mostra todos os eventos marcados\n\n"
        "Envios agendados:\n"
        "🕑 Segunda-feira às 9h: eventos da semana\n"
        "🕑 Todos os dias às 12h: eventos do dia, caso haja\n"
    )

    await reply_message(message, update)
