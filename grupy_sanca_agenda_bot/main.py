from grupy_sanca_agenda_bot.bot import bot
from grupy_sanca_agenda_bot.database import init_db


def main():
    init_db()
    bot()


if __name__ == "__main__":
    main()
