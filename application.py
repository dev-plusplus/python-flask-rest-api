import os

from flask import Flask, request, abort, g
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
from cerberus import Validator
from os import environ
import jwt

from decorators import auth_decorator
from utils import serialize_mongo_id

load_dotenv()

schema = {"name": {"type": "string"}, "description": {"type": "string"}, "completedAt": {"type": "string"}}
validator: Validator = Validator(schema)

application = Flask(__name__)
# Connect to Mongo
client = pymongo.MongoClient(environ.get('URI'))
task_database = client['TasksDatabase']
task_collection = task_database['TasksCollection']
user_collection = task_database['UsersCollection']


@application.route('/')
def hello():
    return 'Hello World!'


@application.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email", None)
    password = data.get("password", None)
    if email is None or password is None:
        abort(400)
    query_filter = {"email": email, "password": password}
    user = user_collection.find_one(query_filter)
    if user is None:
        abort(404)

    sanitized_user = serialize_mongo_id(user)
    payload = {"id": sanitized_user.get('_id'), "email": sanitized_user.get("email")}
    token = jwt.encode(payload, environ.get('SECRET'), algorithm="HS256")
    return {"token": token}


@application.route('/tasks', methods=['GET', 'POST'])
@auth_decorator
def tasks_view():
    if g.user is None:
        abort(403)

    if request.method == 'GET':
        tasks_cursor = task_collection.find({})
        tasks = []
        for task in tasks_cursor:
            tasks.append(serialize_mongo_id(task))
        return tasks

    if request.method == 'POST':
        data = request.get_json()
        is_valid = validator.validate(data)
        if is_valid is False:
            return validator.errors
        # insert_one modifies the input object to set the _id when you don't put an _id
        task_collection.insert_one(data)
        serialize_mongo_id(data)
        return data


@application.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_decorator
def task_view(task_id):
    if g.user is None:
        abort(403)
    _task_id = ObjectId(task_id)
    if request.method == 'GET':
        task = task_collection.find_one({"_id": _task_id})
        return serialize_mongo_id(task)

    if request.method == 'PUT':
        new_task = request.get_json()
        task_collection.update_one({"_id": _task_id}, {"$set": new_task})
        return new_task

    if request.method == 'DELETE':
        task_collection.delete_one({"_id": _task_id})
        return {"response": True}


if __name__ == '__main__':
    application.run()