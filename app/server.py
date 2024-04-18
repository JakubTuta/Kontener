import uuid

import api
import flask
import flask_session
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = flask.Flask("__name__", template_folder="app/templates")
openai = None
database_base_url = "http://localhost:4001"


def init_sessions(mongo):
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = mongo
    app.config["SESSION_MONGODB_DB"] = "gierka"
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"

    flask_session.Session(app)


def get_mongo_client():
    uri = f"mongodb://admin:password@localhost:27017"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    return mongo


def init_mongo():
    session_id = flask.session.get("session_id")

    response = requests.post(
        f"{database_base_url}/init-mongo",
        json={"doc_id": session_id},
    )

    if response.status_code == 200:
        print("Mongo initialized")
    else:
        print("Error initializing mongo")


def get_messages():
    session_id = flask.session.get("session_id")

    response = requests.post(
        f"{database_base_url}/get-messages",
        json={"doc_id": session_id},
    )

    messages = []

    if response.status_code == 200:
        messages = response.json()
    elif response.status_code == 202:
        print("No messages in database")
    else:
        print("Error while fetching messages")

    return messages


def save_message_in_database(question, answer):
    session_id = flask.session.get("session_id")

    db_question = question.replace("<br>", "\n")
    new_message = {"question": db_question, "answer": answer}

    requests.post(
        f"{database_base_url}/push-to-mongo",
        json={"message": new_message, "doc_id": session_id},
    )


def set_session_id():
    session_id = flask.session.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        flask.session["session_id"] = session_id


@app.route("/")
def index():
    set_session_id()

    global openai
    openai = api.Api()

    init_mongo()

    messages = get_messages()

    if len(messages) == 0:
        previous_question = openai.init_assistant(messages)

        flask.session["previous_question"] = previous_question

    return flask.redirect("/game")


@app.route("/game")
def game():
    previous_question = flask.session.get("previous_question", "")

    messages = get_messages()

    messages = map(
        lambda data_object: {
            "question": data_object["question"].replace("\n", "<br>"),
            "answer": data_object["answer"],
        },
        messages,
    )

    return flask.render_template(
        "game.html", messages=messages, previous_question=previous_question
    )


@app.route("/send_answer", methods=["POST"])
def send_answer():
    question = flask.session.get("previous_question", "")
    answer = flask.request.form.get("answer", "")

    save_message_in_database(question, answer)

    new_question = openai.send_answer(answer)
    flask.session["previous_question"] = new_question

    return flask.redirect("/game")


if __name__ == "__main__":
    mongo = get_mongo_client()
    init_sessions(mongo)

    app.run(port=4000)
