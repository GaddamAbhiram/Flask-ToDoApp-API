from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.app_context().push()


api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)


class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(1000))

db.create_all()


parser = reqparse.RequestParser()
parser.add_argument(
    "task", type=str, help="Task has to be filled", required=True)
parser.add_argument("summary", type=str,
                    help="Summary has to be filled", required=True)

parser_update = reqparse.RequestParser()
parser_update.add_argument("task", type=str)
parser_update.add_argument("summary", type=str)


resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String

}


class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message="Task not present !")
        return task

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = parser.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409, message="Task Present for given ID !")

        todo = TodoModel(
            id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = parser.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()

        if not task:
            abort(404, message="Task not Present ! Can't Update")
        if args['task']:
            task.task = args['task']
        if args['summary']:
            task.summary = args['summary']
        db.session.commit()
        return task

    def delete(self, todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        db.session.delete(task)
        return 'Deleted Successfully !', 204


class TodoList(Resource):
    def get(self):
        tasks = TodoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"tasks": task.task, "summary": task.summary}
        return todos


api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(TodoList, '/todos')
if __name__ == '__main__':
    app.run(debug=True)
