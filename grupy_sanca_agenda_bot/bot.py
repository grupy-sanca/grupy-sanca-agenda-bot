from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os


load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")


def get_html_content(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.text
    else:
        print("Failed to retrieve the page - status code: {response.status_code}")
        exit(1)


def load_events(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    events = []

    for event in soup.select('div[id^="e-"]'):
        title = event.select_one(".ds-font-title-3").get_text(strip=True)
        date_time = event.select_one("time").get_text(strip=True)
        location = event.select_one(".text-gray6").get_text(strip=True)
        description = (
            event.select_one(".utils_cardDescription__1Qr0x").get_text(strip=True)
            if event.select_one(".utils_cardDescription__1Qr0x")
            else None
        )
        link = event.find("a", href=True)["href"]

        events.append(
            {
                "title": title,
                "date_time": date_time,
                "location": location,
                "description": description,
                "link": link,
            }
        )

    return events


async def proximo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    html_content = get_html_content(URL)
    events = load_events(html_content)

    if events:
        event = events[0]
        message = (
            f"*📅 Próximo Evento:* {event['title']}\n"
            f"*🕒 Data e Hora:* {event['date_time']}\n"
            f"*📍 Local:* {event['location']}\n"
        )
        if event.get("description"):
            message += f"*📝 Descrição:*\n{event['description']}\n"

        message += f"🔗 [Clique aqui para se inscrever no Meetup]({event['link']})"
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("Não temos eventos agendados.")


async def agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    html_content = get_html_content(URL)
    events = load_events(html_content)

    if events:
        message = "*📅 Próximos Eventos:*\n"
        for event in events:
            message += f"➡️ [{event['title']}]({event['link']})\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("Não temos eventos agendados.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 *Confira os eventos do grupy-sanca!* 🤖\n\n"
        "⚙️ /agenda: exibe todos os eventos agendados no Meetup\n"
        "⚙️ /proximo: exibe os detalhes do próximo evento agendado.\n"
    )
    await update.message.reply_text(message, parse_mode="Markdown")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("proximo", proximo))
    application.add_handler(CommandHandler("agenda", agenda))

    application.run_polling()


if __name__ == "__main__":
    main()
