import uuid

import flask
import flask_session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

collection = None

app = flask.Flask("__name__")


def get_mongo_client():
    uri = f"mongodb://admin:password@localhost:27017"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    global collection
    collection = mongo.gierka.session_data

    return mongo


def init_sessions(mongo):
    app.config["SESSION_TYPE"] = "mongodb"
    app.config["SESSION_MONGODB"] = mongo
    app.config["SESSION_MONGODB_DB"] = "gierka"
    app.config["SESSION_MONGODB_COLLECT"] = "sessions"

    flask_session.Session(app)


@app.route("/init-mongo", methods=["GET"])
def init_mongo():
    try:
        session_id = flask.session.get("session_id")

        if not session_id:
            session_id = str(uuid.uuid4())
            flask.session["session_id"] = session_id

        collection.update_one(
            {"_id": session_id}, {"$setOnInsert": {"data": []}}, upsert=True
        )

        return "OK", 200

    except:
        return "Error", 400


@app.route("/get-messages", methods=["GET"])
def get_messages():
    try:
        session_id = flask.session.get("session_id")

        document = collection.find_one({"_id": session_id})

        messages = document["data"]

        return messages, 200

    except TypeError:
        return "Empty", 202

    except:
        return "Error", 400


@app.route("/push-to-mongo", methods=["POST"])
def push_to_mongo():
    try:
        data = flask.request.get_json(force=True)

        session_id = flask.session.get("session_id")

        query = {"_id": session_id}
        new_element = {"$push": {"data": data}}

        collection.update_one(query, new_element)

        return "OK", 200

    except:
        return "Error", 400


if __name__ == "__main__":
    mongo = get_mongo_client()
    init_sessions(mongo)

    app.run(port=4001)
