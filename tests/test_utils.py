from datetime import datetime
from unittest import mock

import pytest
from freezegun import freeze_time

from grupy_sanca_agenda_bot.settings import settings
from grupy_sanca_agenda_bot.utils import (
    check_is_period_valid,
    filter_events,
    format_event_message,
    reply_message,
    send_message,
    slice_events,
)


@pytest.mark.parametrize(
    "period,response",
    [
        ("hoje", True),
        ("semanal", True),
        ("mensal", True),
        ("agenda", True),
        ("test", False),
    ],
)
async def test_check_is_period_valid(period, response):
    assert check_is_period_valid(period) is response


async def test_send_message():
    mock_application = mock.MagicMock()
    mock_application.bot = mock.MagicMock()
    mock_application.bot.send_message = mock.AsyncMock()

    await send_message("test message", mock_application)
    mock_application.bot.send_message.assert_awaited_once_with(
        chat_id=settings.GROUP_CHAT_ID,
        message_thread_id=settings.GROUP_CHAT_TOPIC_ID,
        text="test message",
        parse_mode="Markdown",
    )


async def test_send_message_no_topic():
    mock_application = mock.MagicMock()
    mock_application.bot = mock.MagicMock()
    mock_application.bot.send_message = mock.AsyncMock()

    with mock.patch.object(settings, "GROUP_CHAT_TOPIC_ID", None):
        await send_message("test message", mock_application)
        mock_application.bot.send_message.assert_awaited_once_with(
            chat_id=settings.GROUP_CHAT_ID,
            message_thread_id=None,
            text="test message",
            parse_mode="Markdown",
        )


async def test_reply_message():
    mock_update = mock.MagicMock()
    mock_update.message = mock.MagicMock()
    mock_update.message.reply_text = mock.AsyncMock()

    await reply_message("test reply", mock_update)
    mock_update.message.reply_text.assert_awaited_once_with("test reply", parse_mode="Markdown")


@freeze_time("2025-10-10 08:00:00", tz_offset=-3)
def test_filter_events_mensal():
    events = [
        {"date_time": datetime.fromisoformat("2025-10-10T10:00:00-03:00"), "title": "Evento 1"},
        {"date_time": datetime.fromisoformat("2025-10-20T10:00:00-03:00"), "title": "Evento 2"},
        {"date_time": datetime.fromisoformat("2025-07-05T10:00:00-03:00"), "title": "Evento 3"},
    ]
    filtered = filter_events(events, period="mensal")
    assert len(filtered) == 2
    assert all(event["title"] in ["Evento 1", "Evento 2"] for event in filtered)


@freeze_time("2025-10-10 08:00:00", tz_offset=-3)
def test_filter_events_semanal():
    events = [
        {"date_time": datetime.fromisoformat("2025-10-10T10:00:00-03:00"), "title": "Evento 1"},
        {"date_time": datetime.fromisoformat("2025-10-11T10:00:00-03:00"), "title": "Evento 2"},
        {"date_time": datetime.fromisoformat("2025-10-20T10:00:00-03:00"), "title": "Evento 3"},
    ]
    filtered = filter_events(events, period="semanal")
    assert len(filtered) == 2
    assert all(event["title"] in ["Evento 1", "Evento 2"] for event in filtered)


@freeze_time("2025-10-10 08:00:00", tz_offset=-3)
def test_filter_events_hoje():
    print(datetime.now())
    events = [
        {"date_time": datetime.fromisoformat("2025-10-10T10:00:00-03:00"), "title": "Evento 1"},
        {"date_time": datetime.fromisoformat("2025-10-11T15:00:00-03:00"), "title": "Evento 2"},
        {"date_time": datetime.fromisoformat("2025-10-12T10:00:00-03:00"), "title": "Evento 3"},
    ]
    filtered = filter_events(events, period="hoje")
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Evento 1"


@pytest.mark.parametrize(
    "events,slice_size",
    [
        (
            [
                {"title": "Evento 1"},
                {"title": "Evento 2"},
                {"title": "Evento 3"},
                {"title": "Evento 4"},
            ],
            2,
        ),
        ([{"title": "Evento 1"}, {"title": "Evento 2"}], 1),
        ([{"title": "Evento 1"}], 5),
        ([], 3),
    ],
)
def test_slice_events(events, slice_size):
    sliced = slice_events(events, slice_size)
    assert len(sliced) == min(len(events), slice_size)


def test_format_event_message_with_description():
    events = [
        {
            "title": "Evento 1",
            "date_time": datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            "location": "Local 1",
            "description": "Descrição1",
            "link": "http://example.com/event1",
        },
    ]
    message = format_event_message(events, header="Próximo Evento", description=True)
    assert message == (
        "*📅 Próximo Evento:*\n\n"
        "*Evento 1*\n\n"
        "*🕒 Data e Hora:* 10/10/2025 às 10h00\n"
        "*📍 Local:* Local 1\n\n"
        "*📝 Descrição:*\nDescrição1\n\n"
        "🔗 [Clique aqui para se inscrever no evento](http://example.com/event1)\n\n"
    )


def test_format_event_message_without_description():
    events = [
        {
            "title": "Evento 1",
            "date_time": datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            "location": "Local 1",
            "description": "Descrição1",
            "link": "http://example.com/event1",
        },
        {
            "title": "Evento 2",
            "date_time": datetime.fromisoformat("2025-10-11T15:00:00-03:00"),
            "location": "Local 2",
            "description": "Descrição2",
            "link": "http://example.com/event2",
        },
    ]
    message = format_event_message(events, header="Agenda Mensal", description=False)
    assert message == (
        "*📅 Agenda Mensal:*\n\n"
        "*Evento 1*\n\n"
        "*🕒 Data e Hora:* 10/10/2025 às 10h00\n"
        "*📍 Local:* Local 1\n\n"
        "🔗 [Clique aqui para se inscrever no evento](http://example.com/event1)\n\n"
        "*Evento 2*\n\n"
        "*🕒 Data e Hora:* 11/10/2025 às 15h00\n"
        "*📍 Local:* Local 2\n\n"
        "🔗 [Clique aqui para se inscrever no evento](http://example.com/event2)\n\n"
    )
