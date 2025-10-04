from unittest import mock

from freezegun import freeze_time

from grupy_sanca_agenda_bot.commands import agenda, force_update, next
from grupy_sanca_agenda_bot.settings import settings


@mock.patch("grupy_sanca_agenda_bot.commands.delete_cache")
async def test_force_update_no_admin(mock_delete_cache):
    mock_update = mock.MagicMock()
    mock_update.message.from_user.id = 999
    await force_update(mock_update, mock.Mock())
    mock_delete_cache.assert_not_called()


@mock.patch("grupy_sanca_agenda_bot.commands.delete_cache")
async def test_force_update_is_admin(mock_delete_cache):
    mock_update = mock.MagicMock()
    mock_update.message.from_user.id = settings.ADMINS[0]
    await force_update(mock_update, mock.Mock())
    mock_delete_cache.assert_called_once_with()


@mock.patch("grupy_sanca_agenda_bot.commands.delete_cache")
@mock.patch("grupy_sanca_agenda_bot.commands.settings")
async def test_force_update_empty_admin(mock_settings, mock_delete_cache):
    mock_settings.ADMINS = None
    mock_update = mock.MagicMock()
    mock_update.message.from_user.id = settings.ADMINS[0]
    await force_update(mock_update, mock.Mock())
    mock_delete_cache.assert_not_called()


@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_next_with_events(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    message = (
        "*📅 Próximo Evento:*\n\n"
        f"*{events[0]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[0]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[0]['location']}\n\n"
        f"*📝 Descrição:*\n{events[0]['description']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[0]['link']})\n\n"
    )
    await next(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_next_no_events(mock_load_events, mock_reply_message):
    mock_load_events.return_value = []
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    await next(mock_update, mock_context)
    mock_reply_message.assert_called_once_with("Sem próximos eventos", mock_update)


@freeze_time("2024-07-01 08:00:00")
@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_events(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = []
    message = (
        "*📅 Agenda:*\n\n"
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
        f"*{events[3]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[3]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[3]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[3]['link']})\n\n"
    )
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@freeze_time("2024-07-01 08:00:00")
@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_no_events(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = []
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = []
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with("Sem próximos eventos", mock_update)


@freeze_time("2024-07-01 08:00:00")
@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_events_mensal(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = ["mensal"]
    message = (
        "*📅 Agenda mensal:*\n\n"
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
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@freeze_time("2024-07-15 08:00:00")
@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_events_semanal(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = ["semanal"]
    message = (
        "*📅 Agenda semanal:*\n\n"
        f"*{events[1]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[1]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[1]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[1]['link']})\n\n"
        f"*{events[2]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[2]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[2]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[2]['link']})\n\n"
    )
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@freeze_time("2024-08-05 08:00:00")
@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_events_hoje(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = ["hoje"]
    message = (
        "*📅 Agenda hoje:*\n\n"
        f"*{events[3]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[3]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[3]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[3]['link']})\n\n"
    )
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_digit_period(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = ["2"]
    message = (
        "*📅 Próximos 2 eventos na agenda:*\n\n"
        f"*{events[0]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[0]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[0]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[0]['link']})\n\n"
        f"*{events[1]['title']}*\n\n"
        f"*🕒 Data e Hora:* {events[1]['date_time'].strftime('%d/%m/%Y às %Hh%M')}\n"
        f"*📍 Local:* {events[1]['location']}\n\n"
        f"🔗 [Clique aqui para se inscrever no evento]({events[1]['link']})\n\n"
    )
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(message, mock_update)


@mock.patch("grupy_sanca_agenda_bot.commands.reply_message")
@mock.patch("grupy_sanca_agenda_bot.commands.event_extractor.load_events")
async def test_agenda_with_wrong_period(mock_load_events, mock_reply_message, events):
    mock_load_events.return_value = events
    mock_update = mock.MagicMock()
    mock_context = mock.Mock()
    mock_context.args = ["invalid"]
    await agenda(mock_update, mock_context)
    mock_reply_message.assert_called_once_with(
        "Valor inválido, escolha entre: mensal, semanal, hoje, ou passe um número inteiro positivo",
        mock_update,
    )
