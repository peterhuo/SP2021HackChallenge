import json
import os
from db import db
from flask import Flask
from flask import request 
from db import User, Talent, Need, Asset

# define db filename
db_filename = "talentExchange.db"
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

# for Authentication Purpose 
def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def get_user_by_username(username):
    return User.query.filter(User.name == name).first()

def get_user_by_session_token(session_token):
    return User.query.filter(User.session_token == session_token).first()

def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token == update_token).first()

def extract_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, json.dumps({"error": "Missing auth header"})
    
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, json.dumps({"error": "Invalid auth header"})

    return True, bearer_token 

@app.route("/register/", methods=["POST"])
def register_account():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")
    username = body.get("username")
    if email is None or password is None or username is None:
        return failure_response("Missing Information :(")
    
    optional_user = get_user_by_email(email)

    if optional_user is not None:
        return failure_response("User already exist :( Please sign in or use another email address.")
    
    new_user = User(
        email = email,
        password = password,
        username = username
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize_authen(), 201)

@app.route("/login/", methods=["POST"])
def login():
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")
    if email is None or password is None:
        return failure_response("Missing Information :(")
    
    user = get_user_by_email(email)
    if user is None:
        return failure_response("User not found :( Please sign up first or check if your email is correct.")
    elif user.verify_password(password) == False:
        return failure_response("Incorrect password :(")
    else:
        return success_response(user.serialize_authen(), 201)
    
@app.route("/session/", methods=["POST"])
def update_session():
    success, update_token = extract_token(request)
    if not success:
        return update_token
    
    user = get_usre_by_update_token(update_token)

    if user is None:
        return json.dumps({"error": f"Invalid update token: {update_token}"})
    
    user.renew_session()
    db.session.commit()

    return success_response(user.serialize_authen(), 201)

@app.route("/users/") 
def get_users():
    return success_response([u.serialize() for u in User.query.all()])

@app.route("/users/", methods=["POST"]) # This endpoint and function may not be used anymore
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
    user = User.query.filter_by(id= user_id).first()
    if user is None:
        return failure_response("User not found :(")
    all_users = User.query.all()
    matches = []
    for u in all_users:
        if user.check(u) == 3:
            matches.append(u)
    return success_response([u.serialize() for u in matches])

@app.route("/users/<int:user_id>/talent_match/")
def talent_match(user_id):
    user = User.query.filter_by(id= user_id).first()
    if user is None:
        return failure_response("User not found :(")
    all_users = User.query.all()
    matches = []
    for u in all_users:
        if user.check(u) == 2:
            matches.append(u)
    return success_response([u.serialize() for u in matches])

@app.route("/users/<int:user_id>/need_match/")
def need_match(user_id):
    user = User.query.filter_by(id= user_id).first()
    if user is None:
        return failure_response("User not found :(")
    all_users = User.query.all()
    matches = []
    for u in all_users:
        if user.check(u) == 1:
            matches.append(u)
    return success_response([u.serialize() for u in matches])

@app.route("/users/<int:user_id>/others")
def others(user_id):
    user = User.query.filter_by(id= user_id).first()
    if user is None:
        return failure_response("User not found :(")
    all_users = User.query.all()
    matches = []
    for u in all_users:
        if user.check(u) == 0:
            matches.append(u)
    return success_response([u.serialize() for u in matches])


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
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


#-- IMAGE ROUTES --------------------------------------------------
@app.route("/users/<int:user_id>/profile/")
def get_profile_by_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    user.asset = Asset.query.filter_by(user_id = user_id)
    return success_response([a.serialize() for a in user.asset])

@app.route("/users/<int:user_id>/profile/upload/", methods=["POST"])
def upload(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    if len(user.asset) > 0:
        return failure_response("There already is a profile picture")
    body = json.loads(request.data)
    image_data = body.get('image_data')
    if image_data is None:
        return failure_response('No Image!')
    asset = Asset(
        image_data = image_data,
        user_id = user_id    
    )
    db.session.add(asset)
    db.session.commit()
    return success_response(asset.serialize(), 201)

@app.route("/users/<int:user_id>/<int:asset_id>/profile/delete/", methods=["DELETE"])
def delete_profile(user_id, asset_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found :(")
    profile = Asset.query.filter_by(id=asset_id).first()
    if profile is None:
        return failure_response("Profile picture not found :(")
    db.session.delete(profile)
    db.session.commit()
    return success_response(user.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
