from ..models import Device, User, UserDevice, DeviceAssignmentLog, \
    AccessNode
from ..model_enums import (
    DeviceTypeEnum,
    UserRoleEnum,
    DeviceStatusEnum,
    UserStatusEnum
)
from ..app import db
from ..app import app
from ..role_required import role_required
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
from sqlalchemy import exc
from werkzeug import exceptions
from ..query.device_access_logs import device_access_logs
from ..utils.array_to_csv_flask_response import array_to_csv_flask_response

devices = Blueprint('devices', __name__)


# create a new device
@app.route("/api/devices", methods=["POST"])
@jwt_required()
def create_device():
    role_required([UserRoleEnum.ADMIN])

    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()
    status = request.json.get("status", None).strip()

    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    # validate optional status parameter
    if (status):
        valid_status = status in [e.value for e in DeviceStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # create
        device = Device(type=type, name=name)
        if (status):
            device.status = status
        db.session.add(device)
        db.session.commit()

        # get full data
        db.session.refresh(device)

        return jsonify(
            id=device.id,
            name=device.name,
            type=device.type,
            status=device.status,
            createdAt=device.created_at.isoformat()
        )
    except exc.IntegrityError:
        abort(409, 'a device with that name already exists')
    except Exception:
        abort(500, 'an unknown error occurred')


# update a device
@app.route("/api/devices/<device_id>", methods=["PUT"])
@jwt_required()
def update_device(device_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()
    status = request.json.get("status", None).strip()

    if (not device_id):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')

    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    # validate optional status parameter
    if (status):
        valid_status = status in [e.value for e in DeviceStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # find
        device = Device.query.filter_by(id=device_id).first()

        if device is None:
            abort(404, 'unable to find a device with that id')

        # update
        device.type = type
        device.name = name
        device.status = status
        db.session.commit()

        # return the latest data in database
        db.session.refresh(device)
        return jsonify(
            id=device.id,
            name=device.name,
            type=device.type,
            createdAt=device.created_at.isoformat()
        )
    except exceptions.NotFound:
        abort(404, 'unable to find a device with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# archive a device
@app.route("/api/devices/<device_id>", methods=["DELETE"])
@jwt_required()
def archive_device(device_id):
    role_required([UserRoleEnum.ADMIN])

    if (not device_id):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')

    try:
        # find
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id')

        # archive device
        device.status = DeviceStatusEnum.ARCHIVED
        db.session.commit()

        # clear device from assigned node
        node = AccessNode.query.filter(
            AccessNode.device_id == device.id
        ).first()
        if node:
            node.device_id = None
            db.session.commit()

        # clear user assignments to device
        UserDevice.query.filter(
            UserDevice.device_id == device.id
        ).delete()
        db.session.commit()

        return jsonify(message='device archived')
    except exceptions.NotFound:
        abort(404, 'unable to find a device with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of devices
@app.route("/api/devices", methods=["GET"])
@jwt_required()
def read_devices():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    # CSV download?
    content_type = request.headers.get('Content-Type')

    # set order by
    order_by = Device.name
    match request.args.get('orderBy'):
        case 'date':
            order_by = Device.created_at
        case 'type':
            order_by = Device.type
        case 'status':
            order_by = Device.status

    query = Device.query

    # filter by device type
    if request.args.get('type'):
        valid_type = request.args.get('type') \
            in [e.value for e in DeviceTypeEnum]
        if (valid_type):
            query = query.filter(Device.type == request.args.get('type'))

    # filter by status
    if request.args.get('status'):
        valid_status = request.args.get('status') \
            in [e.value for e in DeviceStatusEnum]
        if (valid_status):
            query = query.filter(Device.status == request.args.get('status'))

    # filter by user id
    if request.args.get('userId'):
        query = query.join(
            UserDevice, UserDevice.device_id == Device.id, isouter=True
        ).filter(UserDevice.assigned_to_user_id == request.args.get('userId'))

    # hide archived if no status set
    if not request.args.get('status'):
        query = query.filter(Device.status != DeviceStatusEnum.ARCHIVED)

    # TODO: filter by user assignment (with table join, once users have
    # assignments to test)

    # set order direction
    if request.args.get('orderDir') == 'desc':
        order_by = order_by.desc()

    # page
    page = 1
    if (request.args.get('page')):
        page = int(request.args.get('page'))
        print(page)

    # TODO: consider a server default config, also for a max page count
    per_page = app.config['DEFAULT_PER_PAGE']
    max_per_page = app.config['DEFAULT_MAX_PER_PAGE']
    if (request.args.get('perPage')):
        per_page = int(request.args.get('perPage'))

    results = query \
        .order_by(order_by) \
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=False
        )

    devices = []
    for device in results:
        devices.append({
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'status': device.status,
            'createdAt': device.created_at.isoformat()
        })

    if content_type == 'text/csv':
        return array_to_csv_flask_response(devices)
    return jsonify(devices=devices)


# get a single device including full device information and associated data
# useful for a UI detail page and related reporting
@app.route("/api/devices/<device_id>", methods=["GET"])
@jwt_required()
def read_device_view(device_id):
    if (not device_id):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')

    try:
        # find
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id')

        # access node with device assigned
        access_node = AccessNode.query.filter_by(device_id=device_id).first()
        access_node_res = {}
        if access_node:
            access_node_res = {
                'id': access_node.id,
                'type': access_node.type,
                'name': access_node.name,
                'mac_address': access_node.mac_address,
                'status': access_node.status,
                'last_accessed_user_id': access_node.last_accessed_user_id,
                'last_accessed_at': access_node.last_accessed_at,
                'device_id': access_node.device_id,
                'created_at': access_node.created_at
            }

        # users with access to device
        device_users = db.session.query(
            User.id,
            User.first_name,
            User.last_name
        ) \
            .join(UserDevice, User.id == UserDevice.assigned_to_user_id) \
            .filter_by(device_id=device_id) \
            .order_by(User.last_name, User.first_name)
        device_users_res = []
        for device_user in device_users:
            user_obj = {
                'id': device_user.id,
                'firstName': device_user.first_name,
                'lastName': device_user.last_name
            }
            device_users_res.append(user_obj)

        access_logs = device_access_logs(
            {
                'per_page': app.config['DEFAULT_PER_PAGE'],
                'device_id': device_id,
            }
        )

        view = {
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'createdAt': device.created_at.isoformat(),
            'status': device.status,
            'accessNode': access_node_res,
            'deviceUsers': device_users_res,
            'accessHistory': access_logs
        }

        return jsonify(view=view)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')


# assign device to user
@app.route("/api/devices/<device_id>/assign", methods=["POST"])
@jwt_required()
def assign_device(device_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    user_id = request.json.get("userId", None)

    if (not device_id):
        abort(
            422,
            'missing device id e.g. /api/devices/DEVICE-ID/assign'
        )

    if (not user_id):
        abort(
            422,
            'missing user id'
        )

    try:
        # find device that is also active
        device = Device.query.filter_by(
            id=device_id,
            status=DeviceStatusEnum.AVAILABLE
        ).first()
        if not device:
            abort(404, 'unable to find an active device with that id')

        # find user that is also active
        user = User.query.filter_by(
            id=user_id,
            status=UserStatusEnum.ACTIVE
        ).first()
        if not user:
            abort(404, 'unable to find a user with that id')

        # don't assign if already assigned to device
        user_device = UserDevice.query.filter_by(
            assigned_to_user_id=user_id,
            device_id=device_id
        ).first()
        if user_device:
            abort(409, 'user already assigned to this device')

        # assign device to user
        user_device = UserDevice(
            device_id=device_id,
            assigned_to_user_id=user_id,
            assigned_by_user_id=current_user.id

        )
        db.session.add(user_device)
        db.session.commit()

        # log device change
        device_assignment_log = DeviceAssignmentLog(
            device_id=device_id,
            assigned_to_user_id=user_device.assigned_to_user_id,
            assigned_by_user_id=user_device.assigned_by_user_id,
        )
        db.session.add(device_assignment_log)
        db.session.commit()

        return jsonify(message='device assigned')
    except exceptions.Conflict as err:
        abort(409, err)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')


# unassign device to user
@app.route("/api/devices/<device_id>/unassign", methods=["DELETE"])
@jwt_required()
def unassign_device(device_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    user_id = request.json.get("userId", None)

    if (not device_id):
        abort(
            422,
            'missing device id e.g. /api/devices/DEVICE-ID/assign'
        )

    if (not user_id):
        abort(
            422,
            'missing user id'
        )

    try:
        # find device assignment
        user_device = UserDevice.query.filter_by(
            device_id=device_id,
            assigned_to_user_id=user_id
        ).first()
        if not user_device:
            abort(404, 'unable to find an active device assignment with \
                  that user id and device id')

        # find device
        device = Device.query.filter_by(
            id=device_id,
        ).first()
        if not device:
            abort(404, 'unable to find a device with that id')

        # find user
        user = User.query.filter_by(
            id=user_id
        ).first()
        if not user:
            abort(404, 'unable to find a user with that id')

        # unassign card from user
        db.session.delete(user_device)
        db.session.commit()

        # log device change
        device_assignment_log = DeviceAssignmentLog(
            device_id=device_id,
            unassigned_from_user_id=user_id,
            assigned_by_user_id=user_device.assigned_by_user_id
        )
        db.session.add(device_assignment_log)
        db.session.commit()

        return jsonify(message='device unassigned')
    except exceptions.Conflict as err:
        abort(409, err)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')
