import uuid
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Enum
from sqlalchemy.sql import func
from .model_enums import UserRoleEnum, AccessCardStatusEnum, \
    AccessNodeStatusEnum, DeviceTypeEnum, DeviceStatusEnum, \
    UserEmergeAccessLevelEnum, UserStatusEnum, UserAccessActionEnum, \
    AccessNodeScanActionEnum


def uuid_str():
    return str(uuid.uuid4())


# TODO: Cleanup script needed for tokens older than x days
class TokenBlocklist(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    jti = db.Column(
        db.String(36),
        nullable=False,
        index=True
    )
    type = db.Column(
        db.String(10),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


# TODO: How do we want to handle first admin user? Perhaps first registration?
# (just no default 'admin' with 'admin' password please!)
class User(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )
    first_name = db.Column(
        db.String(100),
    )
    last_name = db.Column(
        db.String(100),
    )
    emerge_access_level = db.Column(
        Enum(UserEmergeAccessLevelEnum),
        default=UserEmergeAccessLevelEnum.FULL_DAY_ACCESS
    )
    _password = db.Column(
        "password",
        db.String(256),
        nullable=False
    )
    # TEMP: setting ADMIN by default for dev purposes, UNVERIFIED needs to be
    # set once there's a method to verify etc.
    role = db.Column(
        Enum(UserRoleEnum),
        nullable=False,
        default=UserRoleEnum.ADMIN
    )
    status = db.Column(
        Enum(UserStatusEnum),
        nullable=False,
        default=UserStatusEnum.ACTIVE
    )
    last_logged_in_at = db.Column(
        db.DateTime,
        nullable=True
    )
    last_updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )
    last_updated_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)


class UserEditLog(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    role = db.Column(
        Enum(UserRoleEnum),
        nullable=False
    )
    status = db.Column(
        Enum(UserStatusEnum),
        nullable=False
    )
    emerge_access_level = db.Column(
        Enum(UserEmergeAccessLevelEnum),
        nullable=True,
    )
    updated_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        # This is nullable because on register there is no active user yet
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class UserAccessLog(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    action = db.Column(
        Enum(UserAccessActionEnum),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class AccessCard(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    card_number = db.Column(
        db.Integer,
        nullable=False
    )
    facility_code = db.Column(
        db.Integer,
        nullable=False,
        default=46
    )
    card_type = db.Column(
        db.Integer,
        nullable=False,
        default=46
    )
    status = db.Column(
        Enum(AccessCardStatusEnum),
        nullable=False,
        default=AccessCardStatusEnum.ACTIVE
    )
    last_updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )
    last_updated_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class EmergeAccessCardStatusCodeLookup(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    status = db.Column(
        Enum(AccessCardStatusEnum),
        nullable=False
    )
    emerge_status_code = db.Column(
        db.Integer,
        nullable=False
    )


class UserAccessCard(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    assigned_to_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    access_card_id = db.Column(
        db.String(36),
        db.ForeignKey('access_card.id'),
        nullable=False,
        index=True
    )
    assigned_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class AccessCardLog(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    access_card_id = db.Column(
        db.String(36),
        db.ForeignKey('access_card.id'),
        nullable=False,
        index=True
    )
    assigned_to_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        index=True
    )
    assigned_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
    )
    status = db.Column(
        Enum(AccessCardStatusEnum),
        nullable=False,
        index=True
    )
    emerge_access_level = db.Column(
        Enum(UserEmergeAccessLevelEnum),
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class Device(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    type = db.Column(
        Enum(DeviceTypeEnum),
        nullable=False
    )
    status = db.Column(
        Enum(DeviceStatusEnum),
        nullable=False,
        default=DeviceStatusEnum.AVAILABLE
    )
    name = db.Column(
        db.String(100),
        unique=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )


class UserDevice(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    device_id = db.Column(
        db.String(36),
        db.ForeignKey('device.id'),
        nullable=False,
        index=True
    )
    assigned_to_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    assigned_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False
    )
    assigned_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class DeviceAssignmentLog(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    device_id = db.Column(
        db.String(36),
        db.ForeignKey('device.id'),
        nullable=False,
        index=True
    )
    assigned_to_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        index=True
    )
    unassigned_from_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        index=True
    )
    assigned_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )


class AccessNode(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    type = db.Column(
        Enum(DeviceTypeEnum),
        nullable=False
    )
    name = db.Column(
        db.String(100),
        unique=True
    )
    mac_address = db.Column(
        db.String(17),
        unique=True,
        nullable=False,
    )
    status = db.Column(
        Enum(AccessNodeStatusEnum),
        nullable=False,
        default=AccessNodeStatusEnum.OFFLINE
    )
    last_accessed_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=True
    )
    last_accessed_at = db.Column(
        db.DateTime,
        nullable=True
    )
    device_id = db.Column(
        db.String(36),
        db.ForeignKey('device.id'),
        nullable=True
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now()
    )


class AccessNodeLog(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        nullable=False,
        index=True,
        default=uuid_str
    )
    user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False,
        index=True
    )
    access_card_id = db.Column(
        db.String(36),
        db.ForeignKey('access_card.id'),
        nullable=False,
        index=True
    )
    access_node_id = db.Column(
        db.String(36),
        db.ForeignKey('access_node.id'),
        nullable=False,
        index=True
    )
    device_id = db.Column(
        db.String(36),
        db.ForeignKey('device.id'),
        nullable=False,
        index=True
    )
    action = db.Column(
        Enum(AccessNodeScanActionEnum),
        nullable=False,
        index=True
    )
    success = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )
    created_by_user_id = db.Column(
        db.String(36),
        db.ForeignKey('user.id'),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )
