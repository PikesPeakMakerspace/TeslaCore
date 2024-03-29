from ..models import TokenBlocklist, User, UserAccessLog
from ..model_enums import UserAccessActionEnum
from ..app import db
from ..app import app
from datetime import datetime
from datetime import timezone
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
import jwt
from .users import write_user_update_log

auth = Blueprint('auth', __name__)


@app.route("/api/auth/register", methods=["POST"])
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    first_name = request.json.get("firstName", None)
    last_name = request.json.get("lastName", None)

    if (not username):
        abort(422, 'missing username')

    if (not password):
        abort(422, 'missing password')

    if (not first_name):
        abort(422, 'missing first name')

    if (not last_name):
        abort(422, 'missing last name')

    # check for existing user
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(message="username already in use"), 401

    # TEMPORARY
    # Only allow one/the first user register as an admin until there's
    # a need to allow multiple users e.g. members to register. For now
    # there's nothing in place to validate or need registrations, yet
    # it's good to have a unique user/pass for the first admin.
    user = User.query.first()
    if user:
        return jsonify(
            message="A user is already registered. For now until there's a \
need, only the first admin user can register. Create new users \
instead in admin."
            ), 401
    # END TEMPORARY

    # Need captcha, email verification, etc.
    new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
    db.session.add(new_user)
    db.session.commit()

    # get full data
    db.session.refresh(new_user)

    # log user update
    write_user_update_log(new_user)

    # log access
    log = UserAccessLog(
        user_id=new_user.id,
        action=UserAccessActionEnum.REGISTER,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(message="registration successful")


@app.route("/api/auth/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify(message="wrong username or password"), 401

    # generate token
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

    # update last login time
    now = datetime.now(timezone.utc)
    db.session.query(User).\
        filter(User.username == username).\
        update({'last_logged_in_at': now})
    db.session.commit()

    # log access
    log = UserAccessLog(
        user_id=user.id,
        action=UserAccessActionEnum.LOGIN,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(accessToken=access_token, refreshToken=refresh_token)


# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    userId = get_jwt_identity()
    user = User.query.filter_by(id=userId).one_or_none()
    access_token = create_access_token(identity=user)
    return jsonify(accessToken=access_token)


# Endpoint for revoking the current users access token. Saved the unique
# identifier (jti) for the JWT into our database.
@app.route("/api/auth/logout", methods=["POST"])
@jwt_required(verify_type=False)
def modify_token():
    # access token in header auth
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
    db.session.commit()

    # refresh token in POST body
    refreshTokenJwt = request.json.get("refreshToken", None)
    if refreshTokenJwt:
        refreshTokenDecoded = jwt.decode(
            refreshTokenJwt,
            options={"verify_signature": False}
        )
        refreshTokenType = refreshTokenDecoded['type']
        refreshTokenJti = refreshTokenDecoded['jti']
        db.session.add(TokenBlocklist(
            jti=refreshTokenJti,
            type=refreshTokenType,
            created_at=now)
        )
        db.session.commit()

    # log access
    log = UserAccessLog(
        user_id=current_user.id,
        action=UserAccessActionEnum.LOGOUT,
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(message="goodbye")


# A blocklisted access token will not be able to access this any more
@app.route("/api/auth/valid", methods=["GET"])
@jwt_required()
def valid():
    return jsonify(message="valid")


@app.route("/api/auth/who-am-i", methods=["GET"])
@jwt_required()
def who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
      id=current_user.id,
      username=current_user.username,
      firstName=current_user.first_name,
      lastName=current_user.last_name
    )
