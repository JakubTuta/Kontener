import json
import uuid

import flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

collection = None


def init_mongo():
    with open("./mongodb_data.json", "r") as file:
        mongodb_project_data = json.load(file)

    uri = f"mongodb+srv://{mongodb_project_data['username']}:{mongodb_project_data['password']}@{mongodb_project_data['project_name']}.7zgayam.mongodb.net/?retryWrites=true&w=majority&appName={mongodb_project_data['project_name']}"

    mongo = MongoClient(uri, server_api=ServerApi("1"))

    global collection
    collection = mongo.gierka.session_data

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
