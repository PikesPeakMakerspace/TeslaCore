from ..app import db
from ..app import app
from ..models import User, UserAccessLog
from ..model_enums import UserAccessActionEnum
from .device_access_logs import validate_date


default_params = {
    'page': 1,
    'per_page': app.config['DEFAULT_PER_PAGE'],
    # updated_by_user_id
    'user_id': None,
    # optional UserAccessActionEnum
    'action': None,
    # optional start date, example: 2023-11-01 (YYYY-MM-DD)
    'start_date': None,
    # optional end date using datetime
    'end_date': None
}


def user_access_logs(params):
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

    # query
    query = db.session.query(
        UserAccessLog.user_id,
        UserAccessLog.action,
        UserAccessLog.created_at,
        User.first_name,
        User.last_name
    ) \
        .join(
            User,
            UserAccessLog.user_id == User.id
        )

    # filter options
    if user_id:
        query = query.filter(
            UserAccessLog.user_id == user_id
        )

    if action:
        valid_action = action in [e.value for e in UserAccessActionEnum]
        if not valid_action:
            raise ValueError('action value is not valid')
        query = query.filter(UserAccessLog.action == action)

    if start_date:
        validate_date(start_date)
        query = query.filter(UserAccessLog.created_at >= start_date)

    if end_date:
        validate_date(end_date)
        query = query.filter(UserAccessLog.created_at <= end_date)

    # sort results (date created descending for now)
    order = UserAccessLog.created_at.desc()
    query = query.order_by(order)

    # run query
    results = query \
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=app.config['DEFAULT_MAX_PER_PAGE'],
            error_out=False
        )

    access_logs = []
    if results:
        for access_log in results:
            access_logs.append({
                'userId': access_log.user_id,
                'userFirstName': access_log.first_name,
                'userLastName': access_log.last_name,
                'action': access_log.action,
                'createdAt': access_log.created_at.isoformat(),
            })

    return access_logs
