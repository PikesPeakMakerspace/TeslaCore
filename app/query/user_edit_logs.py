from ..app import db
from ..models import User, UserEditLog
from ..model_enums import UserRoleEnum, UserStatusEnum, \
    UserEmergeAccessLevelEnum
from .device_access_logs import validate_date
from sqlalchemy.orm import aliased


default_params = {
    'page': 1,
    'per_page': 1000,
    # updated_by_user_id
    'user_id': None,
    # optional UserRoleEnum
    'role': None,
    # optional UserStatusEnum
    'status': None,
    # optional UserEmergeAccessLevelEnum
    'emerge_access_level': None,
    # updated_by_user_id
    'updated_by_user_id': None,
    # optional start date, example: 2023-11-01 (YYYY-MM-DD)
    'start_date': None,
    # optional end date using datetime
    'end_date': None
}


def user_edit_logs(params):
    try:
        page = params['page']
    except Exception:
        page = default_params['page']
    try:
        per_page = params['per_page']
    except Exception:
        per_page = default_params['per_page']
    try:
        user_id = params['user_id']
    except Exception:
        user_id = default_params['user_id']
    try:
        role = params['role']
    except Exception:
        role = default_params['role']
    try:
        status = params['status']
    except Exception:
        status = default_params['status']
    try:
        emerge_access_level = params['emerge_access_level']
    except Exception:
        emerge_access_level = default_params['emerge_access_level']
    try:
        updated_by_user_id = params['updated_by_user_id']
    except Exception:
        updated_by_user_id = default_params['updated_by_user_id']
    try:
        start_date = params['start_date']
    except Exception:
        start_date = default_params['start_date']
    try:
        end_date = params['end_date']
    except Exception:
        end_date = default_params['end_date']

    # join assigned to an by users for their names
    editedUser = aliased(User)
    updatedByUser = aliased(User)
    query = db.session.query(
        UserEditLog.user_id,
        UserEditLog.role,
        UserEditLog.status,
        UserEditLog.emerge_access_level,
        UserEditLog.updated_by_user_id,
        UserEditLog.created_at,
        editedUser.first_name.label('edited_first_name'),
        editedUser.last_name.label('edited_last_name'),
        updatedByUser.first_name.label('updated_by_first_name'),
        updatedByUser.last_name.label('updated_by_last_name')
    ) \
        .join(
            editedUser,
            UserEditLog.user_id == editedUser.id
        ) \
        .join(
            updatedByUser,
            UserEditLog.updated_by_user_id == updatedByUser.id,
            isouter=True
        )

    # filter options
    if user_id:
        query = query.filter(
            UserEditLog.user_id == user_id
        )

    if role:
        valid_role = role in [e.value for e in UserRoleEnum]
        if not valid_role:
            raise ValueError('role value is not valid')
        query = query.filter(UserEditLog.role == role)

    if status:
        valid_status = status in [e.value for e in UserStatusEnum]
        if not valid_status:
            raise ValueError('status value is not valid')
        query = query.filter(UserEditLog.status == status)

    if emerge_access_level:
        valid_level = emerge_access_level in \
            [e.value for e in UserEmergeAccessLevelEnum]
        if not valid_level:
            raise ValueError('emerge access level value is not valid')
        query = query.filter(
            UserEditLog.emerge_access_level == emerge_access_level
        )

    if updated_by_user_id:
        query = query.filter(
            UserEditLog.updated_by_user_id == updated_by_user_id
        )

    if start_date:
        validate_date(start_date)
        query = query.filter(UserEditLog.created_at >= start_date)

    if end_date:
        validate_date(end_date)
        query = query.filter(UserEditLog.created_at <= end_date)

    # sort results (date created descending for now)
    order = UserEditLog.created_at.desc()
    query = query.order_by(order)

    # run query
    results = query \
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=10000,
            error_out=False
        )

    edit_logs = []
    if results:
        for edit_log in results:
            edit_logs.append({
                'userId': edit_log.user_id,
                'userFirstName': edit_log.edited_first_name,
                'userLastName': edit_log.edited_last_name,
                'role': edit_log.role,
                'status': edit_log.status,
                'emergeAccessLevel': edit_log.emerge_access_level,
                'updatedByUserId': edit_log.updated_by_user_id,
                'updatedByUserFirstName': edit_log.updated_by_first_name,
                'updatedByUserLastName': edit_log.updated_by_last_name,
                'createdAt': edit_log.created_at.isoformat(),
            })

    return edit_logs
