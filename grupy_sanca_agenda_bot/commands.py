from telegram import Update
from telegram.ext import ContextTypes

from grupy_sanca_agenda_bot.bot import reply_message, send_events
from grupy_sanca_agenda_bot.events import filter_events, load_events


async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events = load_events()

    if events:
        event = events[0]
        await send_events(
            [event], context.application, header="Próximo Evento", description=True
        )


async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    events = filter_events(load_events(), period="agenda")

    if events:
        await send_events(
            events, context.application, header="Próximos Eventos", description=False
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 *Confira os eventos do grupy-sanca!* 🤖\n\n"
        "⚙️ /agenda: exibe os próximos três eventos agendados no Meetup\n"
        "⚙️ /proximo: exibe os detalhes do próximo evento agendado.\n"
    )

    await reply_message(message, update)
