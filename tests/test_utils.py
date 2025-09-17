import pytest

from grupy_sanca_agenda_bot.utils import check_is_period_valid


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
    assert check_is_period_valid(period) is not response
