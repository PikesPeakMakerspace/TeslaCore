from ..models import AccessNode, Device
from ..model_enums import DeviceTypeEnum, UserRoleEnum, AccessNodeStatusEnum
from .. import db
from .. import app
from ..role_required import role_required
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import jwt_required
from sqlalchemy import exc
from werkzeug import exceptions

access_nodes = Blueprint('access_nodes', __name__)


# create a new access node
@app.route("/api/accessNodes", methods=["POST"])
@jwt_required()
def create_access_node():
    role_required([UserRoleEnum.ADMIN])

    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()
    mac_address = request.json.get("macAddress", None).strip()
    device_id = request.json.get("deviceId", None).strip()

    if (not type or not name or not mac_address):
        abort(422, 'missing type or name or macAddress')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    # validate optional device id if assigned
    if (device_id):
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id to assign')

    try:
        # create
        access_node = AccessNode(
            type=type,
            name=name,
            mac_address=mac_address,
            device_id=device_id
        )
        db.session.add(access_node)
        db.session.commit()

        # get full data
        db.session.refresh(access_node)

        return jsonify(
            id=access_node.id,
            name=access_node.name,
            type=access_node.type,
            macAddress=access_node.mac_address,
            status=access_node.status,
            deviceId=access_node.device_id,
            createdAt=access_node.created_at.isoformat()
        )
    except exc.IntegrityError:
        abort(409, 'an access node with that name already exists')
    except Exception:
        abort(500, 'an unknown error occurred')


# update an access node
@app.route("/api/accessNodes/<access_node_id>", methods=["PUT"])
@jwt_required()
def update_access_node(access_node_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()
    mac_address = request.json.get("macAddress", None).strip()
    device_id = request.json.get("deviceId", None).strip()

    if (not access_node_id):
        abort(422, 'missing device id e.g. /api/accessNodes/NODE-ID')

    if (not type or not name or not mac_address):
        abort(422, 'missing type or name or macAddress')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')

    # validate optional device id if assigned
    if (device_id):
        device = Device.query.filter_by(id=device_id).first()

        if not device:
            abort(404, 'unable to find a device with that id to assign')

    try:
        # find
        access_node = AccessNode.query.filter_by(id=access_node_id).first()

        if not access_node:
            abort(404, 'unable to find an access node with that id')

        # update
        # TODO: do we want to manually update status here?
        access_node.type = type
        access_node.name = name
        access_node.mac_address = mac_address
        access_node.device_id = device_id
        db.session.commit()

        # return the latest data in database
        db.session.refresh(access_node)
        return jsonify(
            id=access_node.id,
            name=access_node.name,
            type=access_node.type,
            macAddress=access_node.mac_address,
            status=access_node.status,
            createdAt=access_node.created_at.isoformat()
        )
    except exceptions.NotFound:
        abort(404, 'unable to find an access node with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# TODO: Consider removing references from other tables once those exist
# archive an access node
@app.route("/api/accessNodes/<access_node_id>", methods=["DELETE"])
@jwt_required()
def archive_access_node(access_node_id):
    role_required([UserRoleEnum.ADMIN])

    if (not access_node_id):
        abort(422, 'missing access node id e.g. /api/accessNodes/NODE-ID')

    try:
        # find
        access_node = AccessNode.query.filter_by(id=access_node_id).first()

        if not access_node:
            abort(404, 'unable to find a device with that id')

        # archive access node
        access_node.status = AccessNodeStatusEnum.ARCHIVED
        db.session.commit()

        # TODO: clear any device assignments to node

        return jsonify(message='access node archived')
    except exceptions.NotFound:
        abort(404, 'unable to find an access node with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of access nodes
@app.route("/api/accessNodes", methods=["GET"])
@jwt_required()
def read_access_nodes():
    # set order by
    order_by = AccessNode.name
    match request.args.get('orderBy'):
        case 'date':
            order_by = AccessNode.created_at
        case 'type':
            order_by = AccessNode.type
        case 'status':
            order_by = AccessNode.status
        case 'macAddress':
            order_by = AccessNode.mac_address

    query = AccessNode.query

    # filter by access node type
    if request.args.get('type'):
        valid_type = request.args.get('type') \
            in [e.value for e in DeviceTypeEnum]
        if (valid_type):
            query = query.filter(
                AccessNode.type == request.args.get('type')
            )

    # filter by status
    if request.args.get('status'):
        valid_status = request.args.get('status') \
            in [e.value for e in AccessNodeStatusEnum]
        if (valid_status):
            query = query.filter(
                AccessNode.status == request.args.get('status')
            )

    # hide archived if no status set
    if not request.args.get('status'):
        query = query.filter(
            AccessNode.status != AccessNodeStatusEnum.ARCHIVED
        )

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

    access_nodes = []
    for access_node in results:
        access_nodes.append({
            'id': access_node.id,
            'name': access_node.name,
            'type': access_node.type,
            'status': access_node.status,
            'macAddress': access_node.mac_address,
            'createdAt': access_node.created_at.isoformat()
        })

    return jsonify(access_nodes=access_nodes)


# get a single access node including full node information and associated data
# useful for a UI detail page and related reporting
@app.route("/api/accessNodes/<access_node_id>", methods=["GET"])
@jwt_required()
def read_access_node_view(access_node_id):
    if (not access_node_id):
        abort(422, 'missing access node id e.g. /api/accessNodes/NODE-ID')

    try:
        # find
        access_node = AccessNode.query.filter_by(id=access_node_id).first()

        if not access_node:
            abort(404, 'unable to find a device with that id')

        view = {
            'id': access_node.id,
            'name': access_node.name,
            'type': access_node.type,
            'macAddress': access_node.mac_address,
            'createdAt': access_node.created_at.isoformat(),
            'status': access_node.status,
            'upTime': 'soon',
            'lastPinged': 'soon',
            'device': {
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


# get access node-centric access logs
# example: access node could have had devices assigned at different times,
# yet people care about how many people use the device, not the node (unless
# curious about the node itself specifically, see this report)
@app.route("/api/accessNodes/<access_node_id>/logs", methods=["GET"])
@jwt_required()
def read_access_node_logs(access_node_id):
    if (not access_node_id):
        abort(422, 'missing access node id e.g. /api/accessNodes/NODE-ID')

    try:
        # find
        access_node = AccessNode.query.filter_by(id=access_node_id).first()

        if not access_node:
            abort(404, 'unable to find a access node with that id')

        # TODO: finish this one after node responses are known

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')
