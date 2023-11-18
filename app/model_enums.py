import enum


# TODO: Discuss: This assumes single role per user. Should we consider a list
# of roles per user? (and how would we go about that if relevant?)
class UserRoleEnum(str, enum.Enum):
    UNVERIFIED = 'unverified'
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'
    # TODO: If a user can access everything a public display can, remove
    # this role?:
    PUBLIC_DISPLAY = 'public display'


class UserStatusEnum(str, enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    ARCHIVED = 'archived'


class AccessCardStatusEnum(str, enum.Enum):
    ACTIVE = 'active'
    LOST = 'lost'
    STOLEN = 'stolen'
    ARCHIVED = 'archived'


class UserEmergeAccessLevelEnum(str, enum.Enum):
    BUSINESS_HOURS_ACCESS = 'business hours access'
    FULL_DAY_ACCESS = 'full day access'
    ADMIN = 'admin'
    BLOCKED = 'blocked'


class UserAccessActionEnum(str, enum.Enum):
    REGISTER = 'register'
    LOGIN = 'login'
    LOGOUT = 'logout'


class AccessNodeStatusEnum(str, enum.Enum):
    OFFLINE = 'offline'
    AVAILABLE = 'available'
    IN_USE = 'in use'
    ERROR = 'error'
    ARCHIVED = 'archived'


class DeviceTypeEnum(str, enum.Enum):
    # TODO: "machine" may be too generalized, make a new enum value for each
    # unique configuration a tesla node needs to work through
    MACHINE = 'machine'
    DOOR = 'door'


class DeviceStatusEnum(str, enum.Enum):
    AVAILABLE = 'available'
    OUT_OF_ORDER = 'out of order'
    OFFLINE = 'offline'
    LOST = 'lost'
    STOLEN = 'stolen'
    ON_LOAN = 'on loan'
    ARCHIVED = 'archived'
