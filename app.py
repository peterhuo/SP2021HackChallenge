import json
import os
from db import db
from flask import Flask
from flask import request 
from db import User, Talent, Need 

# define db filename
db_filename = "todo.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code


# -- USER ROUTES ------------------------------------------------------


@app.route("/")
@app.route("/users/")
def get_uers():
    return success_response([u.serialize() for u in User.query.all()])

@app.route("/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    new_username = body.get("username")
    if new_username is None:
        return failure_response("User account not found :(")
    new_user = User(username=new_username)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/users/<int:user_id>/")
def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    return success_response(user.serialize())

@app.route("/users/<str:user_name>/") #我不是很确定“str” 可不可以这样用
def get_user_by_username(user_name):
    user = User.query.filter_by(username = user_name).first()
    if user is None:
        return failure_response("User not found :(")
    return success_response(user.serialize(), 201)

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(usre_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route("/users/<int:user_id>/", methods=["POST"])
def update_timeavai(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    new_timeavai = body.get("timeavai")
    if new_timeavai is None:
        return failure_response("You did not type in anything :(")
    user.timeavai = new_timeavai
    db.session.commit()
    return success_response(course.serialize())

@app.route("/users/<int:user_id>/", methods=["POST"])
def update_contact(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    new_contact = body.get("contact")
    if new_contact is None:
        return failure_response("You did not type in anything :(")
    user.contact = new_contact
    db.session.commit()
    return success_response(course.serialize())


# -- TALENT ROUTES ---------------------------------------------------


@app.route("/tasks/<int:task_id>/subtasks/", methods=["POST"])
def create_subtask(task_id):
    pass


# -- NEED ROUTES --------------------------------------------------


@app.route("/tasks/<int:task_id>/category/", methods=["POST"])
def assign_category(task_id):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
