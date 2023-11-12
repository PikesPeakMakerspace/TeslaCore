from ..models import Device
from ..model_enums import DeviceTypeEnum, UserRoleEnum, DeviceStatusEnum
from .. import db
from .. import app
from ..role_required import role_required
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import jwt_required
from sqlalchemy import exc

devices = Blueprint('devices', __name__)


# create a new device
@app.route("/api/devices", methods=["POST"])
@jwt_required()
def create_device():
    role_required([UserRoleEnum.ADMIN])

    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()

    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    try:
        # create
        device = Device(type=type, name=name)
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

    if (not device_id):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')

    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    try:
        # find
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id')

        # update
        device.type = type
        device.name = name
        db.session.commit()

        # return the latest data in database
        db.session.refresh(device)
        return jsonify(
            id=device.id,
            name=device.name,
            type=device.type,
            createdAt=device.created_at.isoformat()
        )
    except Exception:
        abort(500, 'an unknown error occurred')


# TODO: Consider removing references from other tables once those exist
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

        # TODO: clear any node to device
        # TODO: clear user assignments to device

        return jsonify(message='device archived')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of devices
@app.route("/api/devices", methods=["GET"])
@jwt_required()
def read_devices():
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
    per_page = 20
    max_per_page = 100
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

        view = {
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'createdAt': device.created_at.isoformat(),
            'status': device.status,
            'accessNode': {
                'id': 'soon',
                'more': 'soon'
            },
            'userRecent': {
                'id': 'soon',
                'more': 'soon',
            },
            'usersWithAccess': [
                {
                    'id': 'soon',
                    'more': 'soon',
                }
            ],
            'accessHistory': [
                {
                    'id': 'soon',
                    'more': 'soon'
                }
            ]
        }

        return jsonify(view=view)
    except Exception:
        abort(500, 'an unknown error occurred')


# get device-centric access logs
# example: device could have had multiple nodes assigned at different times,
# yet people care about how many people use the device, not the node (unless
# curious about the node itself specifically, see access node endpoints)
@app.route("/api/devices/<device_id>/logs", methods=["GET"])
@jwt_required()
def read_device_logs(device_id):
    if (not device_id):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')

    try:
        # find
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id')

        # TODO: finish this one after node responses are known

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')
