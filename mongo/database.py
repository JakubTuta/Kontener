import flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

collections = {}

app = flask.Flask("__name__")


def set_mongo_client():
    uri = f"mongodb://admin:password@mongodb"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    collections["session_data"] = mongo.gierka.session_data
    collections["auth"] = mongo.gierka.auth


def find_user(username):
    query = {"username": username}
    document = collections["auth"].find_one(query)

    return document


def create_new_user(username, password):
    collections["auth"].insert_one(
        {
            "username": username,
            "password": password,
        }
    )


@app.route("/register", methods=["POST"])
def register():
    try:
        data = flask.request.get_json(force=True)

        username = data["username"]
        password = data["password"]

    except:
        return "Error", 400

    user = find_user(username)

    if user:
        return "Error", 400

    create_new_user(username, password)

    return "Ok", 200


@app.route("/login", methods=["POST"])
def login():
    try:
        data = flask.request.get_json(force=True)

        username = data["username"]
        password = data["password"]

    except:
        return "Error", 400

    user = find_user(username)

    if not user:
        return "Error", 400

    if user["password"] != password:
        return "Error", 400

    return "Ok", 200


@app.route("/init-mongo", methods=["POST"])
def init_mongo():
    try:
        data = flask.request.get_json(force=True)
        doc_id = data["doc_id"]

        collections["session_data"].update_one(
            {"_id": doc_id}, {"$setOnInsert": {"data": []}}, upsert=True
        )

        return "OK", 200

    except:
        return "Error", 400


@app.route("/get-messages", methods=["POST"])
def get_messages():
    try:
        data = flask.request.get_json(force=True)
        doc_id = data["doc_id"]

        document = collections["session_data"].find_one({"_id": doc_id})

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

        query = {"_id": data["doc_id"]}
        new_element = {"$push": {"data": data["message"]}}

        collections["session_data"].update_one(query, new_element)

        return "OK", 200

    except:
        return "Error", 400


if __name__ == "__main__":
    set_mongo_client()

    app.run(port=4001, host="0.0.0.0")
