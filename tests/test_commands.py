from unittest import mock

from grupy_sanca_agenda_bot.commands import force_update
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
