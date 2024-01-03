import enum


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
    INACTIVE = 'inactive'
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
    # 0 waiting for card read, tool is off
    IDLE = 'idle'
    # 1 card read, validated, tool is allowed to be turned on
    ENABLED = 'enabled'
    # 2 tool is turned on (if we can track for specific machine)
    IN_USE = 'in use'
    # 3 node error
    ERROR = 'error'
    # 4 not in use currently e.g. long-run 3D printing job is finished
    END_OF_RUN = 'end of run'
    # -1 machine is locked e.g. makerspace emergency, not common
    LOCKDOWN = 'lockdown'
    ARCHIVED = 'archived'


class AccessNodeScanActionEnum(str, enum.Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    HELLO = 'hello'
    ACKNOWLEDGE = 'acknowledge'


class DeviceTypeEnum(str, enum.Enum):
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
