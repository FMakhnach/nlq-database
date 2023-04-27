import os
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from archie.app.conversation import Conversation
from archie.models import ConversationId, Prompt
from archie.ml.audio import try_recognize_text_from_ogg

tg_token = '6203226914:AAHsTEQnref0a4kdF7o0sg3Ba3yQtIdWRus'
api_url = 'http://127.0.0.1:5000/'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    await context.bot.respond(chat_id=update.effective_chat.id, text=f"Your message is: {message}")


async def handle_text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: str = None):
    message = update.message.text
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    try:
        conversation_id = ConversationId(user_id) # TODO more generic
        prompt = Prompt(message)
        conversation = Conversation(conversation_id)
        response = conversation.respond(prompt)
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f'Got ERROR: {e}')


async def voice_to_text(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> str or None:
    ogg_file = f'{file_id}.ogg'
    try:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(ogg_file)
        # TODO language
        text = try_recognize_text_from_ogg(ogg_file)
        return text
    finally:
        if os.path.exists(ogg_file):
            os.remove(ogg_file)


async def handle_voice_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.voice.file_id
    message_text = voice_to_text(file_id, context)
    if message_text is None:
        await context.bot.respond(chat_id=update.effective_chat.id,
                                  text='Failed to recognize voice message, please contact developer.')
        return
    update.message.text = message_text
    await handle_text_msg(update, context)


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
