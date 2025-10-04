from unittest import mock

from freezegun import freeze_time

from grupy_sanca_agenda_bot.scheduler import (
    send_monthly_events,
    send_today_events,
    send_weekly_events,
)


@freeze_time("2024-07-01 09:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_monthly_events_with_events(mock_load_events, mock_send_message, events):
    mock_load_events.return_value = events
    mock_application = mock.MagicMock()
    await send_monthly_events(mock_application)
    message = (
        "*📅 Eventos do Mês:*\n\n"
        f"*{events[0]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[0]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[0]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[0]['link']})\n\n"
        f"*{events[1]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[1]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[1]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[1]['link']})\n\n"
        f"*{events[2]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[2]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[2]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[2]['link']})\n\n"
    )
    mock_send_message.assert_called_once_with(message, mock_application)


@freeze_time("2024-07-01 09:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_monthly_events_without_events(mock_load_events, mock_send_message):
    mock_load_events.return_value = []
    mock_application = mock.MagicMock()
    await send_monthly_events(mock_application)
    mock_send_message.assert_not_called()


@freeze_time("2024-07-15 09:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_weekly_events_with_events(mock_load_events, mock_send_message, events):
    mock_load_events.return_value = events
    mock_application = mock.MagicMock()
    await send_weekly_events(mock_application)
    message = (
        "*📅 Eventos da Semana:*\n\n"
        f"*{events[1]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[1]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[1]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[1]['link']})\n\n"
        f"*{events[2]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[2]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[2]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[2]['link']})\n\n"
    )
    mock_send_message.assert_called_once_with(message, mock_application)


@freeze_time("2024-07-15 09:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_weekly_events_without_events(mock_load_events, mock_send_message):
    mock_load_events.return_value = []
    mock_application = mock.MagicMock()
    await send_weekly_events(mock_application)
    mock_send_message.assert_not_called()


@freeze_time("2024-07-15 12:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_today_events_with_events(mock_load_events, mock_send_message, events):
    mock_load_events.return_value = events
    mock_application = mock.MagicMock()
    await send_today_events(mock_application)
    message = (
        "*📅 Eventos de Hoje:*\n\n"
        f"*{events[1]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[1]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[1]['location']}\n\n"
        f"*📝 Descrição:*\n{events[1]['description']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[1]['link']})\n\n"
    )
    mock_send_message.assert_called_once_with(message, mock_application)


@freeze_time("2024-07-15 12:00:00")
@mock.patch("grupy_sanca_agenda_bot.scheduler.send_message")
@mock.patch("grupy_sanca_agenda_bot.scheduler.event_extractor.load_events")
async def test_send_today_events_without_events(mock_load_events, mock_send_message):
    mock_load_events.return_value = []
    mock_application = mock.MagicMock()
    await send_today_events(mock_application)
    mock_send_message.assert_not_called()
