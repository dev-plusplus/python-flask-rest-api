from flask import Flask, request

app = Flask(__name__)
tasks = []


@app.route('/')
def hello():
    return 'Hello World!'


# CRUD for Tasks
# C = Create Tasks (HTTP POST)
# R = Reading a Task / Reading all the Tasks (HTTP GET)
# U = Update a Task (HTTP PUT)
# D = Delete a Task (HTTP DELETE)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks_view():
    global tasks
    if request.method == 'GET':
        return tasks

    if request.method == 'POST':
        data = request.get_json()
        data['id'] = len(tasks)
        tasks.append(data)
        return data


@app.route('/task/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_view(task_id):
    global tasks
    _task_id = int(task_id)
    if request.method == 'GET':
        return tasks[_task_id]

    if request.method == 'PUT':
        new_task = request.get_json()
        old_task = tasks[_task_id]
        old_task.update(new_task)
        return old_task

    if request.method == 'DELETE':
        del tasks[_task_id]
        return 'OK!'
