from flask import Flask, request
import traceback
from werkzeug.datastructures import FileStorage

from talkql.app.conversation import Conversation
from talkql.ml.audio import try_recognize_text_from_audio
from talkql.models import ConversationId, QueryClass, UserQuery
from talkql.monitoring.logging import log
from talkql.utilities import dict_utils

app = Flask(__name__)

FALLBACK_MESSAGE = 'Простите, у меня произошла ошибка и я не смог обработать Ваш запрос.'


@app.route("/v1/query", methods=["POST"])
def process_text_query():
    try:
        conversation_id = extract_conversation_id_from_request(request.form)
        query = extract_query_from_request(request.form)

        conversation = Conversation(conversation_id)
        response = conversation.respond(query)

        return {
            'response': response.text,
        }
    except Exception as e:
        log(str(e))
        print(traceback.format_exc())
        # TODO graceful degradation
        return {
            'response': FALLBACK_MESSAGE,
        }


@app.route("/v1/query/audio", methods=["POST"])
def process_audio_query():
    try:
        conversation_id = extract_conversation_id_from_request(request.form)
        query = extract_query_from_audio_request(request.files)

        conversation = Conversation(conversation_id)
        response = conversation.respond(query)

        return {
            'recognized_query': query.text,
            'response': response.text,
        }
    except Exception as e:
        log(str(e))
        # TODO graceful degradation
        return {
            'response': FALLBACK_MESSAGE,
        }


@app.route("/v1/user/language", methods=["POST"])
def set_user_language():
    # TODO
    return 'Unimplemented'


def extract_conversation_id_from_request(request_form: dict[str, str]) -> ConversationId:
    key = 'user'
    user = dict_utils.try_get(request_form, key)
    if user is None:
        raise Exception('You did not provide a user id')
    conversation_id = ConversationId(user)  # TODO
    return conversation_id


def extract_query_from_request(request_form: dict[str, str]) -> UserQuery:
    key = 'message'
    message = dict_utils.try_get(request_form, key)
    if message is None:
        raise Exception('You did not provide a message')
    op_hint = extract_operation_hint_from_request(request_form)
    query = UserQuery(message, op_hint)
    return query


def extract_query_from_audio_request(request_files: dict[str, FileStorage]) -> UserQuery:
    key = 'audio'
    if key not in request_files:
        raise Exception('No audio file found')
    audio_file = request_files[key]
    text = try_recognize_text_from_audio(audio_file)
    if text is None:
        raise Exception('Failed to recognize text from audio')
    query = UserQuery(text)
    return query


def extract_operation_hint_from_request(request_form: dict[str, str]) -> QueryClass | None:
    key = 'op_hint'
    op_hint_str = dict_utils.try_get(request_form, key)
    op_hint = QueryClass.from_str(op_hint_str)
    return op_hint


if __name__ == "__main__":
    print('Starting server application')
    app.run(port=80)
