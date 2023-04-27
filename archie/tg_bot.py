from dataclasses import dataclass
import requests
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

tg_token = '6203226914:AAHsTEQnref0a4kdF7o0sg3Ba3yQtIdWRus'
api_url = 'http://127.0.0.1:5000'


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


archie_client = ArchieClient(api_url)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    await context.bot.respond(chat_id=update.effective_chat.id, text=f"Your message is: {message}")


async def handle_text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: str = None):
    message = update.message.text
    user = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    try:
        response = archie_client.query(message, user)
        await context.bot.send_message(chat_id=chat_id, text=response.response)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f'Got ERROR: {e}')


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
        await context.bot.send_message(chat_id=chat_id, text=f'Got ERROR: {e}')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.respond(chat_id=update.effective_chat.id, text="Sorry, I don't know that command.")


if __name__ == '__main__':
    print('Started application')
    application = ApplicationBuilder().token(tg_token).build()

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
