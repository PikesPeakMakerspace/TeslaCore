from ..models import AccessNode, Device, UserAccessCard, AccessCard, \
    AccessNodeLog, User
from ..model_enums import DeviceTypeEnum, UserRoleEnum, \
    AccessNodeStatusEnum, AccessNodeScanActionEnum
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
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')


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
    except exceptions.NotFound as err:
        abort(404, err)
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

        # device assigned to access node
        device = Device.query \
            .filter_by(id=access_node.device_id).first()
        device_res = {}
        if device:
            device_res = {
                'id': device.id,
                'name': device.name,
                'type': device.type,
                'createdAt': device.created_at.isoformat(),
                'status': device.status,
                'accessNode': access_node.id,
            }

        # TODO: this is no longer DRY (don't repeat yourself)
        # recent access history
        access_logs_res = []
        access_logs = db.session.query(
            AccessNodeLog.user_id,
            AccessNodeLog.access_card_id,
            AccessNodeLog.access_node_id,
            AccessNodeLog.device_id,
            AccessNodeLog.access_node_id,
            AccessNodeLog.action,
            AccessNodeLog.success,
            AccessNodeLog.created_by_user_id,
            AccessNodeLog.created_at,
            User.first_name,
            User.last_name,
            Device.name
        ) \
            .join(User, User.id == AccessNodeLog.user_id) \
            .join(Device, Device.id == AccessNodeLog.device_id) \
            .filter(AccessNodeLog.access_node_id == access_node.id) \
            .order_by(AccessNodeLog.created_at.desc()) \
            .limit(100).all()
        if access_logs:
            for access_log in access_logs:
                access_logs_res.append({
                    'userId': access_log.user_id,
                    'userFirstName': access_log.first_name,
                    'userLastName': access_log.last_name,
                    'accessCardId': access_log.access_card_id,
                    'accessNodeId': access_log.access_node_id,
                    'deviceId': access_log.device_id,
                    'deviceName': access_log.name,
                    'action': access_log.action,
                    'success': access_log.success,
                    'createdByUserId': access_log.created_by_user_id,
                    'createdAt': access_log.created_at.isoformat()
                })

        view = {
            'id': access_node.id,
            'name': access_node.name,
            'type': access_node.type,
            'macAddress': access_node.mac_address,
            'createdAt': access_node.created_at.isoformat(),
            'status': access_node.status,
            'device': device_res,
            'accessHistory': access_logs_res
        }

        return jsonify(view=view)
    except exceptions.NotFound as err:
        abort(404, err)
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


# manually scan an access card (override, requires admin jwt auth for now)
@app.route("/api/accessNodes/<access_node_id>/scan", methods=["POST"])
@jwt_required()
def scan_access_node(access_node_id):
    role_required([UserRoleEnum.ADMIN])

    # TODO: consider just setting a user_id here, modeling card scan
    # as REST to start
    access_card_number = request.json.get("accessCardNumber", None)
    action = request.json.get("action", None).strip()

    if (not access_node_id or not access_card_number or not action):
        abort(422, 'missing accessNodeId or accessCardNumber or action')

    valid_action = action \
        in [e.value for e in AccessNodeScanActionEnum]
    if not valid_action:
        abort(422, 'invalid action')

    try:
        # get access node
        access_node = AccessNode.query.filter_by(id=access_node_id).first()
        if not access_node:
            abort(404, 'unable to find an access node with that id')

        # get user access card assignment
        user_access_card = db.session.query(
            UserAccessCard.assigned_to_user_id,
            UserAccessCard.access_card_id
        ) \
            .join(
                AccessCard,
                AccessCard.id == UserAccessCard.access_card_id
            ) \
            .filter_by(card_number=access_card_number) \
            .first()
        if not user_access_card:
            abort(404, 'unable to find a user with that access card id')

        # TODO: consider informing the actual node here via MQTT message

        # write to access log
        access_log = AccessNodeLog(
            user_id=user_access_card.assigned_to_user_id,
            access_card_id=user_access_card.access_card_id,
            access_node_id=access_node.id,
            device_id=access_node.device_id,
            action=action,
            success=True,
            created_by_user_id=current_user.id
        )
        db.session.add(access_log)
        db.session.commit()

        # get full data
        db.session.refresh(access_log)

        return jsonify(
            id=access_log.id,
            userId=access_log.user_id,
            accessCardId=access_log.access_card_id,
            accessNodeId=access_log.access_node_id,
            deviceId=access_log.device_id,
            action=access_log.action,
            success=access_log.success,
            createdByUserId=access_log.created_by_user_id,
            createdAt=access_log.created_at.isoformat()
        )

    except exc.IntegrityError:
        abort(409, 'an access node with that name already exists')
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')
