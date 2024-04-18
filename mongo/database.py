import flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

collection = None

app = flask.Flask("__name__")


def set_mongo_client():
    uri = f"mongodb://admin:password@localhost:27017"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    global collection
    collection = mongo.gierka.session_data


@app.route("/init-mongo", methods=["POST"])
def init_mongo():
    try:
        data = flask.request.get_json(force=True)
        doc_id = data["doc_id"]

        collection.update_one(
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

        document = collection.find_one({"_id": doc_id})

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

        collection.update_one(query, new_element)

        return "OK", 200

    except:
        return "Error", 400


if __name__ == "__main__":
    set_mongo_client()

    app.run(port=4001)
