import uuid
import enum
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum
from sqlalchemy.sql import func

def uuid_str():
    return str(uuid.uuid4())

# TODO: Add when token was set to expire, for a future cleanup script, this will get huge otherwise
class TokenBlocklist(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class UserLevel(str, enum.Enum):
    UNVERIFIED = 'unverified'
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'
    PUBLIC_DISPLAY = 'public display'

# TODO: How do we want to handle first admin user? Perhaps first registration?
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    username = db.Column(db.String(100), unique=True)
    _password = db.Column("password", db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_logged_in_at = db.Column(db.DateTime, nullable=True)
    enabled = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self._password, password)

class AccessCardStatusEnum(str, enum.Enum):
    FUNCTIONAL = 'functional'
    LOST = 'lost'
    STOLEN = 'stolen'
    DECOMMISSIONED = 'decommissioned'

class AccessCard(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    uuid = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    status = db.Column(Enum(AccessCardStatusEnum), nullable=False, default=AccessCardStatusEnum.FUNCTIONAL)
    last_updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_updated_by_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

class UserAccessCard(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    access_card_id = db.Column(db.String(36), db.ForeignKey('access_card.id'), nullable=False)
    assigned_at=db.Column(db.DateTime, nullable=False, server_default=func.now())
    assigned_by_user_id=db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

class DeviceTypeEnum(str, enum.Enum):
    # TODO: "machine" may be too generalized, make a new enum value for each unique configuration a tesla node needs to work through
    MACHINE = 'machine'
    DOOR = 'door'

class Device(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    type = db.Column(Enum(DeviceTypeEnum), nullable=False)
    name = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class UserDevice(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)
    assigned_at=db.Column(db.DateTime, nullable=False, server_default=func.now())
    assigned_by_user_id=db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

class AccessNodeStatusEnum(str, enum.Enum):
    OFFLINE = 'offline'
    AVAILABLE = 'available'
    IN_USE = 'in use'
    ERROR = 'error'
    DECOMMISSIONED = 'decommissioned'

class AccessNode(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    type = db.Column(Enum(DeviceTypeEnum), nullable=False)
    name = db.Column(db.String(100), unique=True)
    mac_address = db.Column(db.String(17), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    status = db.Column(Enum(AccessNodeStatusEnum), nullable=False, default=AccessNodeStatusEnum.OFFLINE)
    last_accessed_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    last_accessed_at = db.Column(db.DateTime, nullable=True)
    # TODO: Discuss: I was going to assign to device via AccessNodeDevice join table, yet I think* nodes will only
    # be assigned to one device at a time. We don't care to keep track when they are assigned or by who. If a device
    # assignment changes, the node type may also need to change at the same time. May I keep here or should this be
    # joined via a join table?
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=True)

class AccessNodeLog(db.Model):
    id = db.Column(db.String(36), primary_key=True, nullable=False, index=True, default=uuid_str)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    access_card_id = db.Column(db.String(36), db.ForeignKey('access_card.id'), nullable=False)
    access_node_id = db.Column(db.String(36), db.ForeignKey('access_node.id'), nullable=False)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)
    success = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # request_id (Do requests have ids in general now? Is it relevant or will it help to log)
    # response_id (Is this an enum or is there an id with this?)
    # message?

# TODO: don't forget user log (login, logout, disable/enable, etc.)
# TODO: access card assignment log
# TODO: machine assignment log