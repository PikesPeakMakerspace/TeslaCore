from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

def uuid_str():
    return str(uuid.uuid4())

# TODO: Add when token was set to expire, for a future cleanup script
class TokenBlocklist(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

# TODO: How do we want to handle first admin user? Perhaps first registration?
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    username = db.Column(db.String(100), unique=True)
    _password = db.Column("password", db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_logged_in = db.Column(db.DateTime, nullable=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self._password, password)