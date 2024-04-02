import json

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

with open("./mongodb_data.json", "r") as file:
    mongodb_project_data = json.load(file)

uri = f"mongodb+srv://{mongodb_project_data['username']}:{mongodb_project_data['password']}@{mongodb_project_data['project_name']}.7zgayam.mongodb.net/?retryWrites=true&w=majority&appName={mongodb_project_data['project_name']}"

client = MongoClient(uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
