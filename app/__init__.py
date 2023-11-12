# TODO: log errors to file

import os
from datetime import timedelta
from flask import Flask
from flask import Response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from json import dumps
from app import models
from app.api.auth import auth as auth_blueprint
from app.api.health import health as health_blueprint
from app.api.devices import devices as devices_blueprint

app = Flask(__name__)
# Set this to something different as environment variable!
app.config["JWT_SECRET_KEY"] = os.environ.get('TESLA_JWT_SECRET_KEY') \
    or "so-help-me-god"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# TODO: no migrations happening yet, finish this
migrate = Migrate(app, db)


# TODO: TEMP: this is pre-migration: create a database based on models if no
# database exists
# TEMP: delete database after model change to recreate (not ideal, enable
# those migrations soon)
with app.app_context():
    db.create_all()

# this is needed for defs like role_required() to work
app.app_context().push()


# TODO: This file getting bigger, can I break out jwt methods here?
# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session \
        .query(models.TokenBlocklist.id) \
        .filter_by(jti=jti) \
        .scalar()
    return token is not None


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = models.User.query.filter_by(id=identity).one_or_none()
    return user


# TODO: this file getting bigger, can I break out error handling methods here?
# TODO: this smells kinda bad, maybe a better way to handle? (e.g. maybe don't
# want to return unknown error as str)
# error handler to return JSON instead of HTML, work kin progress
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.errorhandler(Exception)
def all_exception_handler(error):
    print('all_exception_handler error')
    print(error)

    code = 500
    name = 'unknown'
    message = 'unknown'

    if hasattr(error, 'code'):
        code = error.code
    if hasattr(error, 'error'):
        name = error.error
    if hasattr(error, 'message'):
        message = error.message

    def is_strable(x):
        try:
            str(x)
            return True
        except TypeError:
            return False

    if message == 'unknown' and is_strable(error):
        message = str(error)

    res = {
        "code": code,
        "error": name,
        "message": message,
    }
    return Response(
        status=code,
        mimetype="application/json",
        response=dumps(res)
    )


# API: blueprint for auth endpoints
app.register_blueprint(auth_blueprint)

# API: blueprint for health endpoint
app.register_blueprint(health_blueprint)

# API: blueprint for devices endpoint
app.register_blueprint(devices_blueprint)
