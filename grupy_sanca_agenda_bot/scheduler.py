import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from grupy_sanca_agenda_bot import event_extractor
from grupy_sanca_agenda_bot.utils import (
    PeriodEnum,
    delete_cache,
    filter_events,
    format_event_message,
    send_message,
)


def setup_scheduler(application, loop):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("America/Sao_Paulo"), event_loop=loop)

    scheduler.add_job(
        send_monthly_events,
        "cron",
        day=1,
        hour=9,
        args=[application],
    )

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

    scheduler.add_job(
        delete_cache,
        "cron",
        day_of_week="mon-sun",
        hour=8,
    )

    scheduler.start()


async def send_monthly_events(application):
    events = filter_events(await event_extractor.load_events(), period=PeriodEnum.mensal)
    if events:
        message = format_event_message(events, header="Eventos do Mês", description=False)
        await send_message(message, application)


async def send_weekly_events(application):
    events = filter_events(await event_extractor.load_events(), period=PeriodEnum.semanal)
    if events:
        message = format_event_message(events, header="Eventos da Semana", description=False)
        await send_message(message, application)


async def send_today_events(application):
    events = filter_events(await event_extractor.load_events(), period=PeriodEnum.hoje)
    if events:
        message = format_event_message(events, header="Eventos de Hoje", description=True)
        await send_message(message, application)
