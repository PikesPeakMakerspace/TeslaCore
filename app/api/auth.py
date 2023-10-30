from ..models import TokenBlocklist, User
from .. import db
from .. import app
from datetime import datetime
from datetime import timezone
from flask import jsonify
from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required

auth = Blueprint('api_auth', __name__)

@app.route("/api/auth/register", methods=["PUT"])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # check for existing user
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(msg=f"username already in use"), 401
    
    # TODO: Better improve this so this doesn't get spammed with new users. Need captcha, email verification, etc.
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message="registration successful")

@app.route("/api/auth/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
      return jsonify(msg=f"wrong username or password"), 401
    
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)

# Endpoint for revoking the current users access token. Saved the unique
# identifier (jti) for the JWT into our database.
@app.route("/api/auth/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def modify_token():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
    db.session.commit()
    return jsonify(message=f"{ttype.capitalize()} token successfully revoked")

# A blocklisted access token will not be able to access this any more
@app.route("/api/auth/valid", methods=["GET"])
@jwt_required()
def protected():
    return jsonify(hello="world")