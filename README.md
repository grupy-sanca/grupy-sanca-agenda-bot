# Bot da Agenda do grupy-sanca
Bot desenvolvido para divulgar os eventos do Meetup no grupo do grupy-sanca no Telegram.


## Funcionalidades

### Comandos:
- `/start`: Inicia o bot e mostra os comandos disponíveis
- `/agenda`: Mostra todos os eventos do Meetup no intervalo de 1 ano
- `/proximo`: Mostra o próximo evento do Meetup

#### Comandos de administrador:
- `/force_update`: Força a atualização dos eventos do Meetup, útil para quando um evento é adicionado ou removido manualmente

### Cron Jobs
- **Segunda-feira às 9h**: O bot envia uma mensagem com os eventos da semana
- **Todos os dias às 12h**: O bot envia uma mensagem caso haja um evento no dia

Em grupos com tópicos ativados, é possível definir o tópico onde o bot enviará as mensagens agendadas.

Configure a variável de ambiente `GROUP_CHAT_TOPIC_ID` com o ID do tópico desejado.

## Instruções de desenvolvimento
1. Instale o [uv](https://docs.astral.sh/uv/)
2. Instale as dependências do projeto com o comando `uv sync`
3. Ative o ambiente virtual com o comando `source .venv/bin/activate`
4. Crie um arquivo `.env` na pasta `grupy_sanca_agenda_bot` com as seguintes variáveis de ambiente:
```env
# TOKEN do seu bot gerado pelo BotFather
TELEGRAM_BOT_TOKEN=
# URL do grupo no Meetup onde estão os eventos
MEETUP_GROUP_URL=
# ID do grupo no Telegram onde o bot mandará as mensagens agendadas
GROUP_CHAT_ID=
# ID do tópico do grupo no Telegram onde o bot mandará as mensagens agendadas (opcional)
GROUP_CHAT_TOPIC_ID=
# Lista de IDs de usuários do Telegram que podem usar comandos como o `/force_update` (opcional)
ADMINS=[]
```
5. Rode o bot com o comando `uv run start-bot`
