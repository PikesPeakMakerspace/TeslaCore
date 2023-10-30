from ..models import TokenBlocklist
from .. import db
from .. import app
from datetime import datetime
from datetime import timezone
from flask import jsonify
from flask import Blueprint
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required

auth = Blueprint('api_auth', __name__)

@app.route("/api/auth/login", methods=["POST"])
def login():
    access_token = create_access_token(identity="example_user")
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
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")

# A blocklisted access token will not be able to access this any more
@app.route("/api/auth/valid", methods=["GET"])
@jwt_required()
def protected():
    return jsonify(hello="world")