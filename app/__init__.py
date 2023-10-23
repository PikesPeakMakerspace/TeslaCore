from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sys



# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # TODO: Replace this string with an environment variable
    app.config['SECRET_KEY'] = 'todo-replace-this-with-an-environment-variable'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    from . import models
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # API: blueprint for hello endpoint
    from app.api.hello import hello as hello_blueprint
    app.register_blueprint(hello_blueprint)

    # API: blueprint for auth endpoint
    from app.api.api_auth import api_auth as api_auth_blueprint
    app.register_blueprint(api_auth_blueprint)

    return app