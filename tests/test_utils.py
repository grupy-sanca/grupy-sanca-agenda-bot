from datetime import datetime
from unittest import mock

import pytest
from freezegun import freeze_time

from grupy_sanca_agenda_bot.constants import PeriodEnum
from grupy_sanca_agenda_bot.schemas import Event
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


@freeze_time("2025-10-10 08:00:00")
def test_filter_events_mensal():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição 1",
            location="Local 1",
            link="http://example.com/event1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Evento 2",
            date_time=datetime.fromisoformat("2025-10-20T10:00:00-03:00"),
            description="Descrição 2",
            location="Local 2",
            link="http://example.com/event2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Evento 3",
            date_time=datetime.fromisoformat("2025-07-05T10:00:00-03:00"),
            description="Descrição 3",
            location="Local 3",
            link="http://example.com/event3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.mensal)
    assert len(filtered) == 2
    assert all(event.title in ["Evento 1", "Evento 2"] for event in filtered)


@freeze_time("2025-10-10 08:00:00")
def test_filter_events_semanal():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição 1",
            location="Local 1",
            link="http://example.com/event1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Evento 2",
            date_time=datetime.fromisoformat("2025-10-11T10:00:00-03:00"),
            description="Descrição 2",
            location="Local 2",
            link="http://example.com/event2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Evento 3",
            date_time=datetime.fromisoformat("2025-10-20T10:00:00-03:00"),
            description="Descrição 3",
            location="Local 3",
            link="http://example.com/event3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.semanal)
    assert len(filtered) == 2
    assert all(event.title in ["Evento 1", "Evento 2"] for event in filtered)


@freeze_time("2025-10-10 08:00:00")
def test_filter_events_hoje():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição 1",
            location="Local 1",
            link="http://example.com/event1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Evento 2",
            date_time=datetime.fromisoformat("2025-10-11T10:00:00-03:00"),
            description="Descrição 2",
            location="Local 2",
            link="http://example.com/event2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Evento 3",
            date_time=datetime.fromisoformat("2025-10-12T10:00:00-03:00"),
            description="Descrição 3",
            location="Local 3",
            link="http://example.com/event3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.hoje)
    assert len(filtered) == 1
    assert filtered[0].title == "Evento 1"


@freeze_time("2025-10-10 15:45:00")
def test_filter_events_agenda():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição 1",
            location="Local 1",
            link="http://example.com/event1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Evento 2",
            date_time=datetime.fromisoformat("2025-10-10T16:00:00-03:00"),
            description="Descrição 2",
            location="Local 2",
            link="http://example.com/event2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Evento 3",
            date_time=datetime.fromisoformat("2025-10-12T10:00:00-03:00"),
            description="Descrição 3",
            location="Local 3",
            link="http://example.com/event3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.agenda)
    assert len(filtered) == 2


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
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição1",
            location="Local 1",
            link="http://example.com/event1",
        ),
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
        Event(
            id=None,
            identifier="1",
            title="Evento 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Descrição1",
            location="Local 1",
            link="http://example.com/event1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Evento 2",
            date_time=datetime.fromisoformat("2025-10-11T15:00:00-03:00"),
            description="Descrição2",
            location="Local 2",
            link="http://example.com/event2",
        ),
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


def test_format_event_message_empty_list():
    events = []
    message = format_event_message(events, header="Empty", description=True)
    assert message == "*📅 Empty:*\n\n"


def test_format_event_message_single_event_no_description():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Single Event",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Description",
            location="Location",
            link="http://example.com/event",
        ),
    ]
    message = format_event_message(events, header="Single", description=False)
    assert "*📝 Descrição:*" not in message
    assert "Single Event" in message
    assert "Location" in message


def test_format_event_message_multiple_events_with_description():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Event 1",
            date_time=datetime.fromisoformat("2025-10-10T10:00:00-03:00"),
            description="Desc 1",
            location="Loc 1",
            link="http://example.com/1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Event 2",
            date_time=datetime.fromisoformat("2025-10-11T11:00:00-03:00"),
            description="Desc 2",
            location="Loc 2",
            link="http://example.com/2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Event 3",
            date_time=datetime.fromisoformat("2025-10-12T12:00:00-03:00"),
            description="Desc 3",
            location="Loc 3",
            link="http://example.com/3",
        ),
    ]
    message = format_event_message(events, header="Multiple", description=True)
    assert "Event 1" in message
    assert "Event 2" in message
    assert "Event 3" in message
    assert "Desc 1" in message
    assert "Desc 2" in message
    assert "Desc 3" in message
    assert message.count("*📝 Descrição:*") == 3


def test_slice_events_zero_quantity():
    events = [{"title": "Event 1"}, {"title": "Event 2"}]
    sliced = slice_events(events, 0)
    assert len(sliced) == 0


def test_slice_events_negative_quantity():
    events = [{"title": "Event 1"}, {"title": "Event 2"}]
    sliced = slice_events(events, -1)
    assert len(sliced) == 1


def test_slice_events_empty_list():
    events = []
    sliced = slice_events(events, 5)
    assert len(sliced) == 0


@freeze_time("2025-10-10 08:00:00")
def test_filter_events_mensal_boundary():
    events = [
        Event(
            id=None,
            identifier="1",
            title="First day",
            date_time=datetime.fromisoformat("2025-10-01T00:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Last day",
            date_time=datetime.fromisoformat("2025-10-31T23:59:59-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Next month",
            date_time=datetime.fromisoformat("2025-11-01T00:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.mensal)
    assert len(filtered) == 2
    assert filtered[0].title == "First day"
    assert filtered[1].title == "Last day"


@freeze_time("2025-10-10 08:00:00")
def test_filter_events_semanal_boundary():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Monday",
            date_time=datetime.fromisoformat("2025-10-06T10:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/1",
        ),
        Event(
            id=None,
            identifier="2",
            title="Next Monday",
            date_time=datetime.fromisoformat("2025-10-13T10:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/2",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.semanal)
    assert len(filtered) == 1
    assert filtered[0].title == "Monday"


@freeze_time("2025-10-10 12:00:00")
def test_filter_events_hoje_boundary():
    events = [
        Event(
            id=None,
            identifier="1",
            title="Start of day",
            date_time=datetime.fromisoformat("2025-10-10T00:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/1",
        ),
        Event(
            id=None,
            identifier="2",
            title="End of day",
            date_time=datetime.fromisoformat("2025-10-10T23:59:59-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/2",
        ),
        Event(
            id=None,
            identifier="3",
            title="Tomorrow",
            date_time=datetime.fromisoformat("2025-10-11T00:00:00-03:00"),
            description="Desc",
            location="Loc",
            link="http://example.com/3",
        ),
    ]
    filtered = filter_events(events, period=PeriodEnum.hoje)
    assert len(filtered) == 2
    assert filtered[0].title == "Start of day"
    assert filtered[1].title == "End of day"
