from flask import Flask, render_template, request

from archie.app.conversation import Conversation

# > Application improvements
# [UNNECESSARY] user authentication
# [DONE]: persistent storage
# [DONE]: logging
# TODO: environment configuration
# TODO: secrets
# TODO: docker

# > AI improvements
# TODO: make it not bullshit (impossible)
# [DONE]: make it remember itself
# TODO: memory summarization
# [DONE]: db-side semantic search? https://github.com/pgvector/pgvector -- made it on elastic
# TODO: message sizes restrictions
# TODO: memory time relation
# TODO: remove memories
# [DONE]: embeddings search threshold
# [DONE]: multilanguage
# TODO: reminders (notifications)?
# TODO: validate AI answer and retry?

app = Flask(__name__)
messages = []


@app.route("/")
def home():
    return render_template("index.html", messages=messages)


@app.route("/send", methods=["POST"])
def send():
    user_message = request.form['message']
    user_id = request.form['user'] if 'user' in request.form else 0

    conversation = Conversation(user_id)
    response = conversation.send_message(user_message)

    messages.append({"sender": "user", "content": user_message})
    messages.append({"sender": "bot", "content": response})
    # template = render_template("index.html", messages=messages)
    # return template

    return {
        'message': response
    }


if __name__ == "__main__":
    app.run(debug=True)
