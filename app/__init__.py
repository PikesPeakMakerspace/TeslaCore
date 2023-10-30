from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)
ACCESS_EXPIRES = timedelta(hours=1)
app.config["JWT_SECRET_KEY"] = "super-secret" # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)

# We are using an in memory database here as an example. Make sure to use a
# database with persistent storage in production!
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

# API: blueprint for auth endpoint
from app.api.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# API: blueprint for health endpoint
from app.api.health import health as health_blueprint
app.register_blueprint(health_blueprint)