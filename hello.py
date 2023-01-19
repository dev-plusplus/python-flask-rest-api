from flask import Flask, request
import pymongo
from bson.objectid import ObjectId

from cerberus import Validator

schema = {"name": {"type": "string"}, "description": {"type": "string"}}
validator: Validator = Validator(schema)

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World!'


# Connect to Mongo
client = pymongo.MongoClient("mongodb+srv://demo:123demo123@cluster0.09pkckl.mongodb.net/?retryWrites=true&w=majority")
task_database = client['task_database']
task_collection = task_database['task_collection']
print(client.server_info())


def serialize(mongo_row):
    mongo_row['_id'] = str(mongo_row['_id'])
    return mongo_row


# CRUD for Tasks
# C = Create Tasks (HTTP POST)
# R = Reading a Task / Reading all the Tasks (HTTP GET)
# U = Update a Task (HTTP PUT)
# D = Delete a Task (HTTP DELETE)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():
    if request.method == 'GET':
        tasks_cursor = task_collection.find({})
        tasks = []
        for task in tasks_cursor:
            tasks.append(serialize(task))
        return tasks

    if request.method == 'POST':
        data = request.get_json()
        is_valid = validator.validate(data)
        if is_valid is False:
            return validator.errors
        # insert_one modifies the input object to set the _id when you don't put an _id
        task_collection.insert_one(data)
        serialize(data)
        return data


@app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_view(task_id):
    _task_id = ObjectId(task_id)
    if request.method == 'GET':
        task = task_collection.find_one({"_id": _task_id})
        return serialize(task)

    if request.method == 'PUT':
        new_task = request.get_json()
        task_collection.update_one({"_id": _task_id}, {"$set": new_task})
        return new_task

    if request.method == 'DELETE':
        task_collection.delete_one({"_id": _task_id})
        return {"response": True}
