from ..app import db
from ..models import User, AccessCardLog, AccessCardStatusEnum, \
    UserEmergeAccessLevelEnum
from .device_access_logs import validate_date
from sqlalchemy.orm import aliased


default_params = {
    'page': 1,
    'per_page': 1000,
    # optional user id string
    'assigned_to_user_id': None,
    # optional user id string
    'assigned_by_user_id': None,
    # optional access card id string
    'access_card_id': None,
    # optional AccessCardStatusEnum
    'status': None,
    # optional UserEmergeAccessLevelEnum
    'emerge_access_level': None,
    # optional start date, example: 2023-11-01 (YYYY-MM-DD)
    'start_date': None,
    # optional end date using datetime
    'end_date': None
}


def access_card_edit_logs(params):
    try:
        page = params['page']
    except Exception:
        page = default_params['page']
    try:
        per_page = params['per_page']
    except Exception:
        per_page = default_params['per_page']
    try:
        assigned_to_user_id = params['assigned_to_user_id']
    except Exception:
        assigned_to_user_id = default_params['assigned_to_user_id']
    try:
        assigned_by_user_id = params['assigned_by_user_id']
    except Exception:
        assigned_by_user_id = default_params['assigned_by_user_id']
    try:
        access_card_id = params['access_card_id']
    except Exception:
        access_card_id = default_params['access_card_id']
    try:
        status = params['status']
    except Exception:
        status = default_params['status']
    try:
        emerge_access_level = params['emerge_access_level']
    except Exception:
        emerge_access_level = default_params['emerge_access_level']
    try:
        start_date = params['start_date']
    except Exception:
        start_date = default_params['start_date']
    try:
        end_date = params['end_date']
    except Exception:
        end_date = default_params['end_date']

    # join assigned to an by users for their names
    assignedToUser = aliased(User)
    assignedByUser = aliased(User)

    query = db.session.query(
        AccessCardLog.access_card_id,
        AccessCardLog.assigned_to_user_id,
        AccessCardLog.assigned_by_user_id,
        AccessCardLog.status,
        AccessCardLog.emerge_access_level,
        AccessCardLog.created_at,
        assignedToUser.first_name.label('to_first_name'),
        assignedToUser.last_name.label('to_last_name'),
        assignedByUser.first_name.label('by_first_name'),
        assignedByUser.last_name.label('by_last_name')
    ) \
        .join(
            assignedToUser,
            AccessCardLog.assigned_to_user_id == assignedToUser.id
        ) \
        .join(
            assignedByUser,
            AccessCardLog.assigned_by_user_id == assignedByUser.id
        )

    # filter options
    if assigned_to_user_id:
        query = query.filter(
            AccessCardLog.assigned_to_user_id == assigned_to_user_id
        )

    if assigned_by_user_id:
        query = query.filter(
            AccessCardLog.assigned_by_user_id == assigned_by_user_id
        )

    if access_card_id:
        query = query.filter(
            AccessCardLog.access_card_id == access_card_id
        )

    if status:
        valid_status = status in [e.value for e in AccessCardStatusEnum]
        if not valid_status:
            raise ValueError('status value is not valid')
        query = query.filter(AccessCardLog.status == status)

    if emerge_access_level:
        valid_level = emerge_access_level in \
            [e.value for e in UserEmergeAccessLevelEnum]
        if not valid_level:
            raise ValueError('emerge access level value is not valid')
        query = query.filter(
            AccessCardLog.emerge_access_level == emerge_access_level
        )

    if start_date:
        validate_date(start_date)
        query = query.filter(AccessCardLog.created_at >= start_date)

    if end_date:
        validate_date(end_date)
        query = query.filter(AccessCardLog.created_at <= end_date)

    # sort results (date created descending for now)
    order = AccessCardLog.created_at.desc()
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
                'accessCardId': edit_log.access_card_id,
                'assignedToUserId': edit_log.assigned_to_user_id,
                'assignedToFirstName': edit_log.to_first_name,
                'assignedToLastName': edit_log.to_last_name,
                'assignedByUserId': edit_log.assigned_by_user_id,
                'assignedByFirstName': edit_log.by_first_name,
                'assignedByLastName': edit_log.by_last_name,
                'status': edit_log.status,
                'emergeAccessLevel': edit_log.emerge_access_level,
                'createdAt': edit_log.created_at.isoformat(),
            })

    return edit_logs
