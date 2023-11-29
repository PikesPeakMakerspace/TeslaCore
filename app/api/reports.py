from ..model_enums import UserRoleEnum
from ..app import app
from ..role_required import role_required
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import jwt_required
from ..query.device_access_logs import device_access_logs
from ..query.access_card_edit_logs import access_card_edit_logs
from ..query.user_edit_logs import user_edit_logs
from ..query.user_access_logs import user_access_logs
from ..utils.array_to_csv_flask_response import array_to_csv_flask_response

reports = Blueprint('reports', __name__)


@app.route("/api/reports/deviceAccess", methods=["GET"])
@jwt_required()
def device_access():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    page = request.args.get('page')
    per_page = request.args.get('perPage')
    user_id = request.args.get('userId')
    access_card_id = request.args.get('accessCardId')
    access_node_id = request.args.get('accessNodeId')
    device_id = request.args.get('deviceId')
    action = request.args.get('action')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    content_type = request.headers.get('Content-Type')

    try:
        params = {}

        if page:
            params['page'] = int(page)
        if per_page:
            params['per_page'] = int(per_page)
        if user_id:
            params['user_id'] = user_id
        if access_card_id:
            params['access_card_id'] = access_card_id
        if access_node_id:
            params['access_node_id'] = access_node_id
        if device_id:
            params['device_id'] = device_id
        if action:
            params['action'] = action
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        access_logs = device_access_logs(params)

        if content_type == 'text/csv':
            return array_to_csv_flask_response(access_logs)
        return jsonify(deviceAccessLogs=access_logs)
    except ValueError as err:
        abort(422, err)
    except AttributeError as err:
        abort(422, err)
    except Exception:
        abort(500, 'an unknown error occurred')


@app.route("/api/reports/accessCardEdits", methods=["GET"])
@jwt_required()
def access_card_edits():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    page = request.args.get('page')
    per_page = request.args.get('perPage')
    assigned_to_user_id = request.args.get('assignedToUserId')
    assigned_by_user_id = request.args.get('assignedByUserId')
    access_card_id = request.args.get('accessCardId')
    status = request.args.get('status')
    emerge_access_level = request.args.get('eMergeAccessLevel')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    content_type = request.headers.get('Content-Type')

    try:
        params = {}

        if page:
            params['page'] = int(page)
        if per_page:
            params['per_page'] = int(per_page)
        if assigned_to_user_id:
            params['assigned_to_user_id'] = assigned_to_user_id
        if assigned_by_user_id:
            params['assigned_by_user_id'] = assigned_by_user_id
        if access_card_id:
            params['access_card_id'] = access_card_id
        if access_card_id:
            params['access_card_id'] = access_card_id
        if status:
            params['status'] = status
        if emerge_access_level:
            params['emerge_access_level'] = emerge_access_level
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        logs = access_card_edit_logs(params)

        if content_type == 'text/csv':
            return array_to_csv_flask_response(logs)
        return jsonify(accessCardEditLogs=logs)
    except ValueError as err:
        abort(422, err)
    except AttributeError as err:
        abort(422, err)
    except Exception:
        abort(500, 'an unknown error occurred')


@app.route("/api/reports/userEdits", methods=["GET"])
@jwt_required()
def user_edits():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    page = request.args.get('page')
    per_page = request.args.get('perPage')
    user_id = request.args.get('userId')
    role = request.args.get('role')
    status = request.args.get('status')
    emerge_access_level = request.args.get('eMergeAccessLevel')
    updated_by_user_id = request.args.get('updatedByUserId')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    content_type = request.headers.get('Content-Type')

    try:
        params = {}

        if page:
            params['page'] = int(page)
        if per_page:
            params['per_page'] = int(per_page)
        if user_id:
            params['user_id'] = user_id
        if role:
            params['role'] = role
        if status:
            params['status'] = status
        if emerge_access_level:
            params['emerge_access_level'] = emerge_access_level
        if updated_by_user_id:
            params['updated_by_user_id'] = updated_by_user_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        logs = user_edit_logs(params)

        if content_type == 'text/csv':
            return array_to_csv_flask_response(logs)
        return jsonify(userEditLogs=logs)
    except ValueError as err:
        abort(422, err)
    except AttributeError as err:
        abort(422, err)
    except Exception:
        abort(500, 'an unknown error occurred')


@app.route("/api/reports/userAccess", methods=["GET"])
@jwt_required()
def user_access():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    page = request.args.get('page')
    per_page = request.args.get('perPage')
    user_id = request.args.get('userId')
    action = request.args.get('action')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    content_type = request.headers.get('Content-Type')

    try:
        params = {}

        if page:
            params['page'] = int(page)
        if per_page:
            params['per_page'] = int(per_page)
        if user_id:
            params['user_id'] = user_id
        if action:
            params['action'] = action
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        logs = user_access_logs(params)

        if content_type == 'text/csv':
            return array_to_csv_flask_response(logs)
        return jsonify(userAccessLogs=logs)
    except ValueError as err:
        abort(422, err)
    except AttributeError as err:
        abort(422, err)
    except Exception:
        abort(500, 'an unknown error occurred')
