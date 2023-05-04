from dataclasses import dataclass
from dotenv import load_dotenv
import os
import requests
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ARCHIE_SERVER_HOST = os.getenv('ARCHIE_SERVER_HOST')
FALLBACK_MESSAGE = 'Простите, я не могу вам ответить. Кажется, у меня ведутся какие-то технические работы'


@dataclass
class QueryResponse:
    response: str


@dataclass
class QueryAudioResponse:
    response: str
    recognized_query: str or None


class ArchieClient:
    def __init__(self, host):
        self.host = host

    def query(self, message: str, user: str) -> QueryResponse:
        endpoint = '/v1/query'
        url = self.host + endpoint
        body = {'message': message, 'user': user}
        response = requests.post(url, body)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            response_json = response.json()
            return QueryResponse(
                response=response_json['response'],
            )
        else:
            # TODO remove
            raise Exception(f'Server error. {response.status_code}, {response.content}.')

    def query_audio(self, audio_file_path, user: str) -> QueryAudioResponse:
        endpoint = '/v1/query/audio'
        url = self.host + endpoint
        body = {'user': user}
        files = {'audio': open(audio_file_path, 'rb')}
        response = requests.post(url, body, files=files)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            response_json = response.json()
            return QueryAudioResponse(
                response=response_json['response'],
                recognized_query=response_json['recognized_query'] if 'recognized_query' in response_json else None,
            )
        else:
            # TODO remove
            raise Exception(f'Server error. {response.status_code}, {response.content}.')


archie_client = ArchieClient(ARCHIE_SERVER_HOST)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    greet = """Hello! My name is Archie and I am a Memory Assistant bot. How can I help you?

Привет! Меня зовут Арчи и я помогу вам с хранением вашей информации"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=greet)


async def handle_text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: str = None):
    message = update.message.text
    user = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    try:
        response = archie_client.query(message, user)
        await context.bot.send_message(chat_id=chat_id, text=response.response)
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=chat_id, text=FALLBACK_MESSAGE)


async def handle_voice_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.voice.file_id
    user = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    try:
        voice_file = await context.bot.get_file(file_id)
        voice_file_path = await voice_file.download_to_drive()
        response = archie_client.query_audio(voice_file_path, user)
        voice_file_path.unlink()

        if response.recognized_query is not None:
            await context.bot.send_message(chat_id=chat_id, text=f'> "{response.recognized_query}"')
        await context.bot.send_message(chat_id=chat_id, text=response.response)
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=chat_id, text=FALLBACK_MESSAGE)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Простите, я не знаю такой команды")


if __name__ == '__main__':
    print('Started application')
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Start command
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Actual text requests
    request_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_msg)
    application.add_handler(request_handler)

    voice_handler = MessageHandler(filters.VOICE, handle_voice_msg)
    application.add_handler(voice_handler)

    # Unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
