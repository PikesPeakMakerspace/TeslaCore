import uuid
import enum
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum
from sqlalchemy.sql import func

class DeviceTypeEnum(enum.Enum):
    # TODO: "machine" may be too generalized, make a new enum value for each unique configuration a tesla node needs to work through
    machine = 1
    door = 2

class UserLevel(enum.Enum):
    pre_auth = 1
    user = 2
    editor = 3
    admin = 4

def uuid_str():
    return str(uuid.uuid4())

# TODO: Add when token was set to expire, for a future cleanup script, this will get huge otherwise
class TokenBlocklist(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

# TODO: How do we want to handle first admin user? Perhaps first registration?
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    username = db.Column(db.String(100), unique=True)
    _password = db.Column("password", db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_logged_in = db.Column(db.DateTime, nullable=True)
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self._password, password)

class AccessCard(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    uuid = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class UserAccessCard(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    access_card_id = db.Column(db.String(36), db.ForeignKey('access_card.id'), nullable=False)
class AccessNode(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    type = db.Column(Enum(DeviceTypeEnum))
    name = db.Column(db.String(100), unique=True)
    mac_address = db.Column(db.String(17), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class Device(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    type = db.Column(Enum(DeviceTypeEnum))
    name = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class AccessNodeDevice(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    access_node_id = db.Column(db.String(36), db.ForeignKey('access_node.id'), nullable=False)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)

class UserDevice(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)

class AccessNodeLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    access_card_id = db.Column(db.String(36), db.ForeignKey('access_card.id'), nullable=False)
    access_node_id = db.Column(db.String(36), db.ForeignKey('access_node.id'), nullable=False)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)
    success = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # request_id (Do requests have ids in general now?)
    # response_id (Is this an enum or is there an id with this?)
    # message?

# TODO: don't forget user log (login, logout, disable/enable, etc.)