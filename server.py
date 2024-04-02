import flask
import flask_session

import api
import database

app = flask.Flask("__name__")
collection = None
openai = None


def init_app(mongo):
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = mongo
    app.config["SESSION_MONGODB_DB"] = "gierka"
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"

    flask_session.Session(app)


@app.route("/")
def index():
    global openai
    openai = api.Api()

    database.init_first_data()
    document = database.get_data_document()
    data = document["data"]

    if len(data) == 0:
        previous_question = openai.init_assistant(data)

        flask.session["previous_question"] = previous_question

    return flask.redirect("/game")


@app.route("/game")
def game():
    previous_question = flask.session.get("previous_question", "")

    document = database.get_data_document()
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
    database.add_to_database(new_object)

    response = openai.send_answer(answer)

    flask.session["previous_question"] = response

    return flask.redirect("/game")


if __name__ == "__main__":
    mongo = database.init_mongo()
    init_app(mongo)

    app.run(debug=True)
