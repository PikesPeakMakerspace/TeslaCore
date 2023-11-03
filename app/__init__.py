import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
# Set this to something different as environment variable!
app.config["JWT_SECRET_KEY"] = os.environ.get('TESLA_JWT_SECRET_KEY') or "so-help-me-god"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from . import models
with app.app_context():
    db.create_all()

# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict)-> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(models.TokenBlocklist.id).filter_by(jti=jti).scalar()
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
    return models.User.query.filter_by(id=identity).one_or_none()

# API: blueprint for auth endpoint
from app.api.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# API: blueprint for health endpoint
from app.api.health import health as health_blueprint
app.register_blueprint(health_blueprint)