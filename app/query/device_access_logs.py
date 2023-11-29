from ..app import db
from ..models import Device, User, AccessNodeLog, AccessNodeScanActionEnum
from datetime import datetime


def validate_date(date_string):
    try:
        print(date_string)
        datetime.fromisoformat(date_string)
    except ValueError:
        raise \
            ValueError("Incorrect data format, should be YYYY-MM-DD HH:MM:SS")


default_params = {
    'page': 1,
    'per_page': 1000,
    # optional user id string
    'user_id': None,
    # optional access card id string
    'access_card_id': None,
    # optional access node id string
    'access_node_id': None,
    # optional device id string
    'device_id': None,
    # optional AccessNodeScanActionEnum
    'action': None,
    # optional start date, example: 2023-11-01 (YYYY-MM-DD)
    'start_date': None,
    # optional end date using datetime
    'end_date': None
}


def device_access_logs(params):
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
        access_card_id = params['access_card_id']
    except Exception:
        access_card_id = default_params['access_card_id']
    try:
        access_node_id = params['access_node_id']
    except Exception:
        access_node_id = default_params['access_node_id']
    try:
        device_id = params['device_id']
    except Exception:
        device_id = default_params['device_id']
    try:
        action = params['action']
    except Exception:
        action = default_params['action']
    try:
        start_date = params['start_date']
    except Exception:
        start_date = default_params['start_date']
    try:
        end_date = params['end_date']
    except Exception:
        end_date = default_params['end_date']

    query = db.session.query(
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
        .join(Device, Device.id == AccessNodeLog.device_id)

    # filter options
    if user_id:
        query = query.filter(AccessNodeLog.user_id == user_id)

    if access_node_id:
        query = query.filter(AccessNodeLog.access_node_id == access_node_id)

    if access_card_id:
        query = query.filter(AccessNodeLog.access_card_id == access_card_id)

    if device_id:
        query = query.filter(AccessNodeLog.device_id == device_id)

    if action:
        valid_action = action in [e.value for e in AccessNodeScanActionEnum]
        if not valid_action:
            raise ValueError('action value is not valid')
        query = query.filter(AccessNodeLog.action == action)

    if start_date:
        validate_date(start_date)
        query = query.filter(AccessNodeLog.created_at >= start_date)

    if end_date:
        validate_date(end_date)
        query = query.filter(AccessNodeLog.created_at <= end_date)

    # sort results (date created descending for now)
    order = AccessNodeLog.created_at.desc()
    query = query.order_by(order)

    # run query
    results = query \
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=10000,
            error_out=False
        )

    # generate API-formatted response
    access_logs = []
    if results:
        for access_log in results:
            access_logs.append({
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

    return access_logs
