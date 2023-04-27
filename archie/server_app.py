from flask import Flask, request
from werkzeug.datastructures import FileStorage

from archie.app.conversation import Conversation
from archie.ml.audio import try_recognize_text_from_audio
from archie.models import ConversationId, UserQuery
from archie.monitoring.logging import log

# > Application improvements
# [UNNECESSARY] user authentication
# [DONE]: persistent storage
# [DONE]: logging
# TODO: configuration
# TODO: docker

# > AI improvements
# TODO: make it not bullshit (impossible)
# [DONE]: last messages history
# [DONE]: semantic search
# [DONE]: embeddings search threshold
# [DONE]: multilanguage
# [DONE]: memory time relation
# TODO: message sizes restriction
# TODO: degrade gracefully on exceptions
# TODO: update/delete operations
# TODO: aggregation questions
# TODO: identify general questions

app = Flask(__name__)


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
        # TODO graceful degradation
        return {
            'response': 'I am sorry, I got ill. Can\'t answer to your request :(',
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
            'response': 'I am sorry, I got ill. Can\'t answer to your request :(',
        }


@app.route("/v1/user/language", methods=["POST"])
def set_user_language():
    # TODO
    return 'Unimplemented'


def extract_conversation_id_from_request(request_form: dict[str, str]) -> ConversationId:
    if 'user' not in request_form or request_form['user'].strip() == '':
        raise Exception('You did not provide a user id')
    conversation_id = ConversationId(request_form['user'])
    return conversation_id


def extract_query_from_request(request_form: dict[str, str]) -> UserQuery:
    if 'message' not in request_form or request_form['message'].strip() == '':
        raise Exception('You did not provide a message')
    query = UserQuery(request_form['message'])
    return query


def extract_query_from_audio_request(request_files: dict[str, FileStorage]) -> UserQuery:
    if 'audio' not in request_files:
        raise Exception('No audio file found')
    audio_file = request_files['audio']
    text = try_recognize_text_from_audio(audio_file)
    if text is None:
        raise Exception('Failed to recognize text from audio')
    query = UserQuery(text)
    return query


if __name__ == "__main__":
    print('Starting server application')
    app.run(debug=True)
