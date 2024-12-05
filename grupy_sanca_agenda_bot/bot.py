import logging

from telegram.ext import Application, CommandHandler

from grupy_sanca_agenda_bot.commands import agenda, force_update, next, start
from grupy_sanca_agenda_bot.scheduler import setup_scheduler
from grupy_sanca_agenda_bot.settings import settings

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def bot():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    setup_scheduler(application)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proximo", next))
    application.add_handler(CommandHandler("agenda", agenda))
    application.add_handler(CommandHandler("force_update", force_update))

    application.run_polling()
