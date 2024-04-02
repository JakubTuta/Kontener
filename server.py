import json
import uuid

import flask
import flask_session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import api

app = flask.Flask("__name__")
collection = None
openai = None


def init_app(mongo):
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = mongo
    app.config["SESSION_MONGODB_DB"] = "gierka"
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"

    flask_session.Session(app)


def init_mongo():
    with open("./mongodb_data.json", "r") as file:
        mongodb_project_data = json.load(file)

    uri = f"mongodb+srv://{mongodb_project_data['username']}:{mongodb_project_data['password']}@{mongodb_project_data['project_name']}.7zgayam.mongodb.net/?retryWrites=true&w=majority&appName={mongodb_project_data['project_name']}"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    return mongo


def get_data_document():
    session_id = flask.session.get("session_id")

    document = collection.find_one({"_id": session_id})

    return document


def add_to_database(new_object):
    session_id = flask.session.get("session_id")

    query = {"_id": session_id}
    new_element = {"$push": {"data": new_object}}

    collection.update_one(query, new_element)


def init_first_data():
    session_id = flask.session.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        flask.session["session_id"] = session_id

    collection.update_one(
        {"_id": session_id}, {"$setOnInsert": {"data": []}}, upsert=True
    )


@app.route("/")
def index():
    global openai
    openai = api.Api()

    init_first_data()
    document = get_data_document()
    data = document["data"]

    if len(data) == 0:
        previous_question = openai.init_assistant(data)

        flask.session["previous_question"] = previous_question

    return flask.redirect("/game")


@app.route("/game")
def game():
    previous_question = flask.session.get("previous_question", "")

    document = get_data_document()
    data = document["data"]

    data = map(
        lambda data_object: {
            "question": data_object["question"].replace("\n", "<br>"),
            "answer": data_object["answer"],
        },
        data,
    )

    return flask.render_template(
        "game.html", messages=data, previous_question=previous_question
    )


@app.route("/send_answer", methods=["POST"])
def send_answer():
    question = flask.session.get("previous_question", "")
    answer = flask.request.form.get("answer", "")

    db_question = question.replace("<br>", "\n")

    new_object = {"question": db_question, "answer": answer}
    add_to_database(new_object)

    response = openai.send_answer(answer)

    flask.session["previous_question"] = response

    return flask.redirect("/game")


if __name__ == "__main__":
    mongo = init_mongo()
    init_app(mongo)

    collection = mongo.gierka.session_data

    app.run(debug=True)
