#TODO protect endpoints based on user roles
#TODO filter by node
#TODO filter by user access
#TODO get one machine
#TODO pagination
#TODO sort

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

        return jsonify(id=device.id, name=device.name, type=device.type, created_at=device.created_at.isoformat())
    except exc.IntegrityError:
        abort(409, 'a device with that name already exists')
    except Exception:
        abort(500, 'an unknown error occurred')

@app.route("/api/devices/<deviceId>", methods=["PUT"])
@jwt_required()
def update_device(deviceId):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])
    
    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()

    if (not deviceId):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')
    
    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')
    
    try:
        # find
        device = Device.query.filter_by(id=deviceId).first()

        if not device:
            abort(404, 'unable to find a device with that id')
        
        # update
        device.type = type
        device.name = name
        db.session.commit()

        # return the latest data in database
        db.session.refresh(device)
        return jsonify(id=device.id, name=device.name, type=device.type, created_at=device.created_at.isoformat())
    except Exception:
        abort(500, 'an unknown error occurred')

#TODO: Consider removing reference from other existing tables once those exist 
@app.route("/api/devices/<deviceId>", methods=["DELETE"])
@jwt_required()
def delete_device(deviceId):
    role_required([UserRoleEnum.ADMIN])
    
    if (not deviceId):
        abort(422, 'missing device id e.g. /api/devices/DEVICE-ID')
    
    try:
        # delete
        Device.query.filter(Device.id == deviceId).delete()
        db.session.commit()
        return jsonify(message='device deleted')
    except Exception:
        abort(500, 'an unknown error occurred')

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

    filters = []

    # filter by device type
    if request.args.get('type'):
        valid_type = request.args.get('type') in [e.value for e in DeviceTypeEnum]
        if (valid_type):
            filters.append(Device.type == request.args.get('type'))

    # filter by status
    if request.args.get('status'):
        valid_status = request.args.get('status') in [e.value for e in DeviceTypeEnum]
        if (valid_status):
            filters.append(Device.status == request.args.get('status'))

    print(filters)

    # TODO: filter by user assignment (with table join, once users have assignments to test)

    # set order direction
    if request.args.get('orderDir') == 'desc':
        order_by = order_by.desc()

    # page
    page = 1
    if (request.args.get('page')):
        #print(request.args.get('page'))
        page = int(request.args.get('page'))
        print(page)

    # TODO: consider a server default config, also for a max page count
    per_page = 20
    max_per_page = 100
    if (request.args.get('perPage')):
        per_page = int(request.args.get('perPage'))
    
    # TODO how do I dynamically chain filters with filters array here instead of hard-coded like it is below? 
    results = Device.query \
        .filter(Device.type == DeviceTypeEnum.MACHINE) \
        .filter(Device.status == DeviceStatusEnum.FUNCTIONAL) \
        .order_by(order_by) \
        .paginate(page=page, per_page=per_page, max_per_page=max_per_page, error_out=False)
    
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
