import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from grupy_sanca_agenda_bot.events import (
    filter_events,
    format_event_message,
    load_events,
)
from grupy_sanca_agenda_bot.utils import send_message


def setup_scheduler(application):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/Sao_Paulo"))

    scheduler.add_job(
        send_weekly_events,
        "cron",
        day_of_week="mon",
        hour=9,
        args=[application],
    )

    scheduler.add_job(
        send_today_events,
        "cron",
        day_of_week="mon-sun",
        hour=12,
        args=[application],
    )

    scheduler.start()


async def send_weekly_events(application):
    events = filter_events(await load_events(), period="week")
    if events:
        message = format_event_message(
            events, header="Eventos da Semana", description=False
        )
        await send_message(message, application)


async def send_today_events(application):
    events = filter_events(await load_events(), period="today")
    if events:
        message = format_event_message(
            events, header="Eventos de Hoje", description=True
        )
        await send_message(message, application)
