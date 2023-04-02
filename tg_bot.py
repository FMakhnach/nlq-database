import logging
# import requests
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from conversation import Conversation

tg_token = '6203226914:AAHsTEQnref0a4kdF7o0sg3Ba3yQtIdWRus'
api_url = 'http://127.0.0.1:5000/'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Let's start our tests.")


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'RECEIVED: {update.message.text}')
    body = {
        'message': update.message.text,
        'user': update.effective_user.id,
    }
    # response = requests.post(api_url + '/send', data=body).json()
    response = Conversation(body['user']).send_message(body['message'])
    print(f'RESPONDED: {response}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't know that command.")


if __name__ == '__main__':
    print('Started application')
    application = ApplicationBuilder().token(tg_token).build()

    # Start command
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Actual text requests
    request_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), answer)
    application.add_handler(request_handler)

    # Unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
