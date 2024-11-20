from telegram.ext import Application, CommandHandler

from grupy_sanca_agenda_bot.commands import agenda, next, start
from grupy_sanca_agenda_bot.scheduler import setup_scheduler
from grupy_sanca_agenda_bot.settings import settings


def main():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    setup_scheduler(application)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proximo", next))
    application.add_handler(CommandHandler("agenda", agenda))

    application.run_polling()


if __name__ == "__main__":
    main()
