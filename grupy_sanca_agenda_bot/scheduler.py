import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from grupy_sanca_agenda_bot.bot import send_events
from grupy_sanca_agenda_bot.events import filter_events, load_events


def setup_scheduler(application):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/Sao_Paulo"))

    scheduler.add_job(
        send_weekly_events,
        "cron",
        day_of_week="wed",
        hour=18,
        minute=8,
        args=[application],
    )

    scheduler.add_job(
        send_today_events,
        "cron",
        day_of_week="wed",
        hour=18,
        minute=8,
        args=[application],
    )

    scheduler.start()


async def send_weekly_events(application):
    events = filter_events(load_events(), period="week", description=False)
    await send_events(events, application, header="Eventos da Semana")


async def send_today_events(application):
    events = filter_events(load_events(), period="today", description=False)
    await send_events(events, application, header="Eventos de Hoje")
