from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# TODO: Add when token was set to expire, for a future cleanup script
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class User(db.Model):
    #TODO: I don't recommend integers as primary key, yet let's keep it for the moment while following tutorial.
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    _password = db.Column("password", db.String(256), nullable=False)
    name = db.Column(db.String(1000))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self._password, password)