from ..models import User, UserEditLog
from ..model_enums import UserRoleEnum, UserStatusEnum, \
    UserEmergeAccessLevelEnum
from .. import db
from .. import app
from ..role_required import role_required
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import jwt_required
from sqlalchemy import exc
from flask_jwt_extended import current_user
from datetime import datetime
from datetime import timezone
from werkzeug import exceptions

users = Blueprint('users', __name__)


def write_user_update_log(user):
    # write to user update log
    userEditLog = UserEditLog(
        user_id=user.id,
        role=user.role,
        status=user.status,
        emerge_access_level=user.emerge_access_level,
        updated_by_user_id=user.last_updated_by_user_id
    )
    db.session.add(userEditLog)
    db.session.commit()


# create a new user
@app.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    role_required([UserRoleEnum.ADMIN])

    username = request.json.get("username", None).strip()
    first_name = request.json.get("firstName", None).strip()
    last_name = request.json.get("lastName", None).strip()
    role = request.json.get("role", None).strip()
    emerge_access_level = request.json.get("eMergeAccessLevel", None).strip()
    password = request.json.get("password", None).strip()
    status = request.json.get("status", None).strip()

    if (not username or not password):
        abort(422, 'missing username or password')

    # validate optional role parameter
    if (role):
        valid_role = role in [e.value for e in UserRoleEnum]
        if (not valid_role):
            abort(422, 'invalid role')

    # validate optional emerge_access_level parameter
    # TODO: consider breaking this out to its own linked table is this is very
    # specific to PPM
    if (emerge_access_level):
        valid_access_level = emerge_access_level in \
            [e.value for e in UserEmergeAccessLevelEnum]
        if (not valid_access_level):
            abort(422, 'invalid emerge_access_level')

    # validate optional status parameter
    if (status):
        valid_status = status in [e.value for e in UserStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # create
        user = User(
            username=username,
            password=password,
            last_updated_by_user_id=current_user.id
        )
        if (first_name):
            user.first_name = first_name
        if (last_name):
            user.last_name = last_name
        if (role):
            user.role = role
        if (emerge_access_level):
            user.emerge_access_level = emerge_access_level
        if (status):
            user.status = status
        db.session.add(user)
        db.session.commit()

        # get full data
        db.session.refresh(user)

        # write to user update log
        write_user_update_log(user)

        return jsonify(
            id=user.id,
            username=user.username,
            firstName=user.first_name,
            lastName=user.last_name,
            eMergeAccessLevel=user.emerge_access_level,
            role=user.role,
            status=user.status,
            createdAt=user.created_at.isoformat(),
            lastUpdatedAt=user.last_updated_at.isoformat(),
            lastUpdatedByUserId=user.last_updated_by_user_id,
        )
    except exc.IntegrityError:
        abort(409, 'a user with that name already exists')
    except Exception:
        abort(500, 'an unknown error occurred')


# update a user
@app.route("/api/users/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    username = request.json.get("username", None).strip()
    first_name = request.json.get("firstName", None).strip()
    last_name = request.json.get("lastName", None).strip()
    role = request.json.get("role", None).strip()
    emerge_access_level = request.json.get("eMergeAccessLevel", None).strip()
    password = request.json.get("password", None).strip()
    status = request.json.get("status", None).strip()

    if (not username):
        abort(422, 'missing username')

    # validate optional role parameter
    if (role):
        valid_role = role in [e.value for e in UserRoleEnum]
        if (not valid_role):
            abort(422, 'invalid role')

    # validate optional emerge_access_level parameter
    # TODO: consider breaking this out to its own linked table is this is very
    # specific to PPM
    if (emerge_access_level):
        valid_access_level = emerge_access_level in \
            [e.value for e in UserEmergeAccessLevelEnum]
        if (not valid_access_level):
            abort(422, 'invalid emerge_access_level')

    # validate optional status parameter
    if (status):
        valid_status = status in [e.value for e in UserStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # find
        user = User.query.filter_by(id=user_id).first()

        if user is None:
            abort(404, 'unable to find a user with that id')

        # update
        user.username = username
        user.last_updated_by_user_id = current_user.id
        user.last_updated_at = datetime.now(timezone.utc)
        if (password):
            user.password = password
        if (first_name):
            user.first_name = first_name
        if (last_name):
            user.last_name = last_name
        if (role):
            user.role = role
        if (emerge_access_level):
            user.emerge_access_level = emerge_access_level
        if (status):
            user.status = status
        db.session.commit()

        # TODO: if not ACTIVE status, update card status to match (INACTIVE,
        # SUSPENDED, ARCHIVED)

        db.session.refresh(user)

        # write to user update log
        write_user_update_log(user)

        return jsonify(
            id=user.id,
            username=user.username,
            firstName=user.first_name,
            lastName=user.last_name,
            eMergeAccessLevel=user.emerge_access_level,
            role=user.role,
            status=user.status,
            createdAt=user.created_at.isoformat(),
            lastUpdatedAt=user.last_updated_at.isoformat(),
            lastUpdatedByUserId=user.last_updated_by_user_id,
        )
    except exceptions.NotFound:
        abort(404, 'unable to find a user with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# archive a user
@app.route("/api/users/<user_id>", methods=["DELETE"])
@jwt_required()
def archive_user(user_id):
    role_required([UserRoleEnum.ADMIN])

    if (not user_id):
        abort(422, 'missing user id e.g. /api/users/USER-ID')

    try:
        # find
        user = User.query.filter_by(id=user_id).first()

        if not user:
            abort(404, 'unable to find a user with that id')

        # archive user
        user.status = UserStatusEnum.ARCHIVED
        db.session.commit()

        # write to user update log
        write_user_update_log(user)

        # TODO: update card status to _____
        # TODO: remove device assignments

        return jsonify(message='user archived')
    except exceptions.NotFound:
        abort(404, 'unable to find a user with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of users
@app.route("/api/users", methods=["GET"])
@jwt_required()
def read_users():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    # set order by
    order_by = User.username
    match request.args.get('orderBy'):
        case 'firstName':
            order_by = User.first_name
        case 'lastName':
            order_by = User.last_name
        case 'eMergeAccessLevel':
            order_by = User.emerge_access_level
        case 'date':
            order_by = User.created_at
        case 'role':
            order_by = User.role
        case 'status':
            order_by = User.status

    query = User.query

    # filter by user role
    if request.args.get('role'):
        valid_role = request.args.get('role') \
            in [e.value for e in UserRoleEnum]
        if (valid_role):
            query = query.filter(User.role == request.args.get('role'))

    # filter by status
    if request.args.get('status'):
        valid_status = request.args.get('status') \
            in [e.value for e in UserStatusEnum]
        if (valid_status):
            query = query.filter(User.status == request.args.get('status'))

    # filter by eMerge access level
    if request.args.get('eMergeAccessLevel'):
        valid_access_level = request.args.get('eMergeAccessLevel') \
            in [e.value for e in UserEmergeAccessLevelEnum]
        if (valid_access_level):
            query = query.filter(
                User.emerge_access_level == request.args.get('eMergeAccessLevel') # noqa
            )

    # hide archived if no status set
    if not request.args.get('status'):
        query = query.filter(User.status != UserStatusEnum.ARCHIVED)

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

    users = []
    for user in results:
        users.append({
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'eMergeAccessLevel': user.emerge_access_level,
            'role': user.role,
            'status': user.status,
            'createdAt': user.created_at.isoformat(),
            'lastUpdatedAt': user.last_updated_at.isoformat(),
            'lastUpdatedByUserId': user.last_updated_by_user_id
        })

    return jsonify(users=users)


# get a single user including full user information and associated data
# useful for a UI detail page and related reporting
@app.route("/api/users/<user_id>", methods=["GET"])
@jwt_required()
def read_user_view(user_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    if (not user_id):
        abort(422, 'missing user id e.g. /api/users/USER-ID')

    try:
        # find
        user = User.query.filter_by(id=user_id).first()

        if not user:
            abort(404, 'unable to find a user with that id')

        view = {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'eMergeAccessLevel': user.emerge_access_level,
            'role': user.role,
            'status': user.status,
            'createdAt': user.created_at.isoformat(),
            'lastUpdatedAt': user.last_updated_at.isoformat(),
            'lastUpdatedByUserId': user.last_updated_by_user_id,
            'devices': [
                {
                    'id': 'soon'
                }
            ],
            'devicesRecent': [
                {
                    'id': 'soon'
                }
            ],
            'accessCards': [
                {
                    'id': 'soon'
                }
            ],
            'accessCardsRecent': [
                {
                    'id': 'soon'
                }
            ],
        }

        return jsonify(view=view)
    except Exception:
        abort(500, 'an unknown error occurred')


# get account edit logs
@app.route("/api/users/<user_id>/editLogs", methods=["GET"])
@jwt_required()
def read_user_edit_logs(user_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    if (not user_id):
        abort(422, 'missing user id e.g. /api/users/USER-ID')

    try:
        # find
        user = User.query.filter_by(id=user_id).first()

        if not user:
            abort(404, 'unable to find a user with that id')

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')


# get account access logs
@app.route("/api/users/<user_id>/accessLogs", methods=["GET"])
@jwt_required()
def read_user_access_logs(user_id):
    if (not user_id):
        abort(422, 'missing user id e.g. /api/users/USER-ID')

    try:
        # find
        user = User.query.filter_by(id=user_id).first()

        if not user:
            abort(404, 'unable to find a user with that id')

        # TODO: finish this one after node responses are known

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')