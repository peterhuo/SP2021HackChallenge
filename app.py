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

# @app.route("/users/<str:user_name>/") #我不是很确定“str” 可不可以这样用
# def get_user_by_username(user_name):
#     user = User.query.filter_by(username = user_name).first()
#     if user is None:
#         return failure_response("User not found :(")
#     return success_response(user.serialize(), 201)

@app.route("/users/<int:user_id>/perfect/")
def perfect(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found :(")
    all_users = User.query.all()
    matches = []
    for u in all_users:
        if user.check(u) == 3:
            matchers.append(u)
    return success_response([u.serialize() for u in matches])

@app.route("/users/<int:user_id>/talent_match/")
def talent_match(user_id):
    pass

@app.route("/users/<int:user_id>/need_match/")
def need_match(user_id):
    pass

@app.route("/users/<int:user_id>/others")
def others(user_id):
    pass


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(usre_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

@app.route("/users/timeavai/<int:user_id>/", methods=["POST"])
def update_timeavai(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    new_timeavai = body.get("timeavai",)
    if new_timeavai is None:
        return failure_response("You did not type in anything :(")
    user.timeavai = new_timeavai
    db.session.commit()
    return success_response(user.serialize())

@app.route("/users/contact/<int:user_id>/", methods=["POST"])
def update_contact(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    new_contact = body.get("contact",)
    if new_contact is None:
        return failure_response("You did not type in anything :(")
    user.contact = new_contact
    db.session.commit()
    return success_response(user.serialize())
    

# -- TALENT ROUTES ---------------------------------------------------


@app.route("/talents/")
def get_all_talents():
    return success_response([t.serialize() for t in Talent.query.all()])

@app.route("/users/<int:user_id>/talents/")
def get_all_talents_byid(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    user.talent = Talent.query.filter_by(user_id = user_id)
    return success_response([t.serialize() for t in user.talent])

@app.route("/users/<int:user_id>/talents/", methods=["POST"])
def create_talent(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    talent = body.get("talent")
    if talent is None:
        return failure_response("You did not type in anything :(")
    new_talent = Talent(
        talent = talent,
        user_id = user_id
    )
    db.session.add(new_talent)
    db.session.commit()
    return success_response(new_talent.serialize())

@app.route("/users/talents/<int:user_id>/<int:talent_id>/", methods=["DELETE"])
def delete_talent(user_id, talent_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    talent = Talent.query.filter_by(id=talent_id).first()
    if talent is None:
        return failure_response("Talent not found :(")
    db.session.delete(talent)
    db.session.commit()
    return success_response(talent.serialize())

@app.route("/users/talents/<int:user_id>/<int:talent_id>/", methods=["POST"])
def update_experience(user_id, talent_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    talent = Talent.query.filter_by(id=talent_id).first()
    if talent is None:
        return failure_response("Talent not foubd :(")
    body = json.loads(request.data)
    new_experience = body.get("experience")
    if new_experience is None:
        return failure_response("You did not type in anything :(")
    talent.experience = new_experience
    db.session.commit()
    return success_response(talent.serialize())

# -- NEED ROUTES --------------------------------------------------


@app.route("/needs/")
def get_all_needs():
    return success_response([n.serialize() for n in Need.query.all()])

@app.route("/users/<int:user_id>/needs/")
def get_all_needs_byid(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    user.need = Need.query.filter_by(user_id = user_id)
    return success_response([n.serialize() for n in user.need])

@app.route("/users/<int:user_id>/needs/", methods=["POST"])
def create_need(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    body = json.loads(request.data)
    need = body.get("need")
    if need is None:
        return failure_response("You did not type in anything :(")
    new_need = Need(
        need = need,
        user_id = user_id 
    )
    db.session.add(new_need)
    db.session.commit()
    return success_response(new_need.serialize())

@app.route("/users/needs/<int:user_id>/<int:need_id>/", methods=["DELETE"])
def delete_need(user_id, need_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    need = Talent.query.filter_by(id=need_id).first()
    if need is None:
        return failure_response("Need not found :(")
    db.session.delete(need)
    db.session.commit()
    return success_response(need.serialize())

@app.route("/users/needs/<int:user_id>/<int:need_id>/", methods=["POST"])
def update_issue(user_id, need_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    need = Need.query.filter_by(id=need_id).first()
    if need is None:
        return failure_response("Need not foubd :(")
    body = json.loads(request.data)
    new_issue = body.get("issue")
    if new_issue is None:
        return failure_response("You did not type in anything :(")
    talent.issue = new_issue
    db.session.commit()





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
