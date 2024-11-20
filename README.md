# Bot da Agenda do grupy-sanca
Bot desenvolvido para divulgar os eventos do Meetup no grupo do grupy-sanca no Telegram.


## Funcionalidades

### Comandos:
- `/start`: Inicia o bot e mostra os comandos disponíveis
- `/agenda`: Mostra todos os eventos do Meetup no intervalo de 1 ano
- `/proximo`: Mostra o próximo evento do Meetup

### Cron Jobs
- **Segunda-feira às 9h**: O bot envia uma mensagem com os eventos da semana
- **Todos os dias às 12h**: O bot envia uma mensagem caso haja um evento no dia

## Instruções de desenvolvimento
1. Instale o [Poetry](https://python-poetry.org/)
2. Instale as dependências do projeto com o comando `poetry install`
3. Ative o ambiente virtual com o comando `poetry shell`
4. Crie um arquivo `.env` na pasta `grupy_sanca_agenda_bot` com as seguintes variáveis de ambiente:
```
TELEGRAM_BOT_TOKEN=<TOKEN do seu bot gerado pelo BotFather>
MEETUP_GROUP_URL=<URL do grupo no Meetup onde estão os eventos>
GROUP_CHAT_ID=<ID do grupo no Telegram onde o bot mandará as mensagens>
```
5. Rode o bot com o comando `poetry run start-bot`

