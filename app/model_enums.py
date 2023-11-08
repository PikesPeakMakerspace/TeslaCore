import enum

# TODO: Discuss: This assumes single role per user. Should we consider a list of roles per user? (and how would we go about that if relevant?)
class UserRoleEnum(str, enum.Enum):
    UNVERIFIED = 'unverified'
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'
    # TODO: If a user can access everything a public display can, remove this role?:
    PUBLIC_DISPLAY = 'public display'

class AccessCardStatusEnum(str, enum.Enum):
    FUNCTIONAL = 'functional'
    LOST = 'lost'
    STOLEN = 'stolen'
    DECOMMISSIONED = 'decommissioned'

class AccessNodeStatusEnum(str, enum.Enum):
    OFFLINE = 'offline'
    AVAILABLE = 'available'
    IN_USE = 'in use'
    ERROR = 'error'
    DECOMMISSIONED = 'decommissioned'

class DeviceTypeEnum(str, enum.Enum):
    # TODO: "machine" may be too generalized, make a new enum value for each unique configuration a tesla node needs to work through
    MACHINE = 'machine'
    DOOR = 'door'

class DeviceStatusEnum(str, enum.Enum):
    FUNCTIONAL = 'functional'
    OUT_OF_ORDER = 'out of order'
    OFFLINE = 'offline'
    LOST = 'lost'
    STOLEN = 'stolen'
    DECOMMISSIONED = 'decommissioned'
    ON_LOAN = 'on loan'