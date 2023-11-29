from ..models import AccessCard, UserAccessCard, User, AccessCardLog
from ..model_enums import AccessCardStatusEnum, UserRoleEnum, \
    UserStatusEnum
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
from sqlalchemy.orm import aliased
from datetime import datetime
from datetime import timezone
from werkzeug import exceptions
from ..query.access_card_edit_logs import access_card_edit_logs
from ..utils.array_to_csv_flask_response import array_to_csv_flask_response

access_cards = Blueprint('access_cards', __name__)


# create a new access card
@app.route("/api/accessCards", methods=["POST"])
@jwt_required()
def create_access_card():
    role_required([UserRoleEnum.ADMIN])

    card_number = int(request.json.get("cardNumber", None))
    facility_code = int(request.json.get("facilityCode", None))
    card_type = int(request.json.get("cardType", None))
    status = request.json.get("status", None).strip()

    if (not card_number):
        abort(422, 'missing cardNumber')

    # don't add the same card more than once
    access_card = AccessCard.query.filter_by(card_number=card_number).first()
    if access_card:
        abort(409, 'an access card with that number already exists')

    # validate optional status if assigned
    if (status):
        valid_status = status in [e.value for e in AccessCardStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # create
        access_card = AccessCard(
            card_number=card_number,
            last_updated_by_user_id=current_user.id
        )

        if (facility_code):
            access_card.facility_code = facility_code
        if (card_type):
            access_card.card_type = card_type
        if (status):
            access_card.status = status
        db.session.add(access_card)
        db.session.commit()

        # get full data
        db.session.refresh(access_card)

        # log access card change
        access_card_log = AccessCardLog(
            access_card_id=access_card.id,
            assigned_by_user_id=current_user.id,
            status=access_card.status
        )
        db.session.add(access_card_log)
        db.session.commit()

        return jsonify(
            id=access_card.id,
            cardNumber=access_card.card_number,
            facilityCode=access_card.facility_code,
            cardType=access_card.card_type,
            status=access_card.status,
            createdAt=access_card.created_at.isoformat(),
            lastUpdatedAt=access_card.last_updated_at.isoformat(),
            lastUpdatedByUserId=access_card.last_updated_by_user_id
        )
    except exc.IntegrityError:
        abort(409, 'an access card with that name already exists')
    except Exception:
        abort(500, 'an unknown error occurred')


# update an access card
@app.route("/api/accessCards/<access_card_id>", methods=["PUT"])
@jwt_required()
def update_access_card(access_card_id):
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    card_number = int(request.json.get("cardNumber", None))
    facility_code = int(request.json.get("facilityCode", None))
    card_type = int(request.json.get("cardType", None))
    status = request.json.get("status", None).strip()

    if (not access_card_id):
        abort(422, 'missing access card id e.g. /api/accessCards/CARD-ID')

    if (not card_number):
        abort(422, 'missing cardNumber')

    # validate optional status if assigned
    if (status):
        valid_status = status in [e.value for e in AccessCardStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # find access card
        access_card = AccessCard.query.filter_by(id=access_card_id).first()
        if not access_card:
            abort(404, 'unable to find an access card with that id')

        # update
        access_card.card_number = card_number
        access_card.facility_code = facility_code
        access_card.card_type = card_type
        access_card.status = status
        access_card.last_updated_by_user_id = current_user.id
        access_card.last_updated_at = datetime.now(timezone.utc)
        db.session.commit()

        # return the latest data in database
        db.session.refresh(access_card)

        # get existing card assignment if applicable
        user_access_card_join_user = UserAccessCard \
            .query \
            .filter_by(
                access_card_id=access_card_id
            ) \
            .join(User, UserAccessCard.assigned_by_user_id == User.id) \
            .first()

        # log access card change
        try:
            assigned_to_user_id = user_access_card_join_user \
                .assigned_to_user_id
        except AttributeError:
            assigned_to_user_id = None
        try:
            emerge_access_level = user_access_card_join_user \
                .emerge_access_level
        except AttributeError:
            emerge_access_level = None
        access_card_log = AccessCardLog(
            access_card_id=access_card.id,
            assigned_to_user_id=assigned_to_user_id,
            assigned_by_user_id=current_user.id,
            status=access_card.status,
            emerge_access_level=emerge_access_level
        )
        db.session.add(access_card_log)
        db.session.commit()

        return jsonify(
            id=access_card.id,
            cardNumber=access_card.card_number,
            facilityCode=access_card.facility_code,
            cardType=access_card.card_type,
            status=access_card.status,
            createdAt=access_card.created_at.isoformat(),
            lastUpdatedAt=access_card.last_updated_at.isoformat(),
            lastUpdatedByUserId=access_card.last_updated_by_user_id
        )
    except exceptions.NotFound:
        abort(404, 'unable to find an access card with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


@app.route("/api/accessCards/<access_card_id>", methods=["DELETE"])
@jwt_required()
def archive_access_card(access_card_id):
    role_required([UserRoleEnum.ADMIN])

    if (not access_card_id):
        abort(422, 'missing access card id e.g. /api/accessCards/CARD-ID')

    try:
        # find access card
        access_card = AccessCard.query.filter_by(id=access_card_id).first()
        if not access_card:
            abort(404, 'unable to find an access card with that id')

        # archive access card
        access_card.status = AccessCardStatusEnum.ARCHIVED
        db.session.commit()

        # clear access card assignments to user if applicable
        user_access_card = UserAccessCard.query.filter_by(
            access_card_id=access_card_id
        ).first()
        if (user_access_card):
            user_access_card.delete()
            db.session.commit()

        # log access card change
        access_card_log = AccessCardLog(
            access_card_id=access_card.id,
            assigned_to_user_id=None,
            assigned_by_user_id=current_user.id,
            status=access_card.status,
            emerge_access_level=None
        )
        db.session.add(access_card_log)
        db.session.commit()

        return jsonify(message='access card archived')

    except exceptions.NotFound:
        abort(404, 'unable to find an access card with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of access cards
@app.route("/api/accessCards", methods=["GET"])
@jwt_required()
def read_access_cards():
    role_required([UserRoleEnum.ADMIN, UserRoleEnum.EDITOR])

    # CSV download?
    content_type = request.headers.get('Content-Type')

    # set order by
    order_by = AccessCard.card_number
    match request.args.get('orderBy'):
        case 'date':
            order_by = AccessCard.created_at
        case 'updatedDate':
            order_by = AccessCard.last_updated_at
        case 'cardType':
            order_by = AccessCard.card_type
        case 'facilityCode':
            order_by = AccessCard.facility_code

    assignedToUser = aliased(User)
    assignedByUser = aliased(User)
    lastUpdatedByUser = aliased(User)
    query = db.session.query(
        AccessCard.id,
        AccessCard.card_number,
        AccessCard.facility_code,
        AccessCard.card_type,
        AccessCard.status,
        AccessCard.created_at,
        AccessCard.last_updated_at,
        AccessCard.last_updated_by_user_id,
        UserAccessCard.assigned_to_user_id,
        UserAccessCard.assigned_by_user_id,
        assignedToUser.first_name.label('to_first_name'),
        assignedToUser.last_name.label('to_last_name'),
        assignedByUser.first_name.label('by_first_name'),
        assignedByUser.last_name.label('by_last_name'),
        lastUpdatedByUser.first_name.label('last_updated_by_first_name'),
        lastUpdatedByUser.last_name.label('last_updated_by_last_name')
    )

    # filter by access card type
    if request.args.get('cardType'):
        card_type = int(request.args.get('cardType'))
        query = query.filter(
            AccessCard.card_type == card_type
        )

    # filter by access card facility code
    if request.args.get('facilityCode'):
        facility_code = int(request.args.get('facilityCode'))
        query = query.filter(
            AccessCard.facility_code == facility_code
        )

    # filter by status
    if request.args.get('status'):
        valid_status = request.args.get('status') \
            in [e.value for e in AccessCardStatusEnum]
        if (valid_status):
            query = query.filter(
                AccessCard.status == request.args.get('status')
            )

    # hide archived if no status set
    if not request.args.get('status'):
        query = query.filter(
            AccessCard.status != AccessCardStatusEnum.ARCHIVED
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

    # join assigned user info
    query = query \
        .join(
            lastUpdatedByUser,
            AccessCard.last_updated_by_user_id == lastUpdatedByUser.id
        ) \
        .join(
            UserAccessCard,
            UserAccessCard.access_card_id == AccessCard.id,
            isouter=True
        ) \
        .join(
            assignedToUser,
            UserAccessCard.assigned_to_user_id == assignedToUser.id,
            isouter=True
        ) \
        .join(
            assignedByUser,
            UserAccessCard.assigned_by_user_id == assignedByUser.id,
            isouter=True
        )

    results = query \
        .order_by(order_by) \
        .paginate(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=False
        )

    access_cards = []
    for access_card in results:
        card_obj = {
            'id': access_card.id,
            'cardNumber': access_card.card_number,
            'facilityCode': access_card.facility_code,
            'cardType': access_card.card_type,
            'status': access_card.status,
            'createdAt': access_card.created_at.isoformat(),
            'lastUpdatedAt': access_card.last_updated_at.isoformat(),
            'lastUpdatedByUserId': access_card.last_updated_by_user_id,
            'lastUpdatedByFirstName': access_card.last_updated_by_first_name,
            'lastUpdatedByLastName': access_card.last_updated_by_last_name,
        }

        # only send assignment values if present
        if access_card.to_first_name:
            card_obj['assignedToFirstName'] = access_card.to_first_name
            card_obj['assignedToLastName'] = access_card.to_last_name
            card_obj['assignedToUserId'] = access_card.assigned_to_user_id
            card_obj['assignedByFirstName'] = access_card.by_first_name
            card_obj['assignedByLastName'] = access_card.by_last_name
            card_obj['assignedByUserId'] = access_card.assigned_by_user_id

        access_cards.append(card_obj)

    if content_type == 'text/csv':
        return array_to_csv_flask_response(access_cards)
    return jsonify(access_cards=access_cards)


# get a single access card associated data useful for a UI detail page and
# related reporting
@app.route("/api/accessCards/<access_card_id>", methods=["GET"])
@jwt_required()
def read_access_card_view(access_card_id):
    if (not access_card_id):
        abort(422, 'missing access card id e.g. /api/accessCards/CARD-ID')

    try:
        # find
        access_card = AccessCard.query \
            .filter_by(id=access_card_id) \
            .first()

        if not access_card:
            abort(404, 'unable to find an access card with that id')

        # get assigned user if assigned
        assigned_user = {}
        user = User.query \
            .join(
                UserAccessCard,
                User.id == UserAccessCard.assigned_to_user_id
            ) \
            .filter_by(access_card_id=access_card_id) \
            .first()
        if user:
            assigned_user = {
                'id': user.id,
                'username': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'eMergeAccessLevel': user.emerge_access_level,
                'role': user.role,
                'status': user.status
            }

        # get assignment history
        assignment_log = access_card_edit_logs(
            {
                'page': 1,
                'per_page': 1000,
                'access_card_id': access_card_id,
            }
        )

        view = {
            'id': access_card.id,
            'cardNumber': access_card.card_number,
            'facilityCode': access_card.facility_code,
            'cardType': access_card.card_type,
            'status': access_card.status,
            'createdAt': access_card.created_at.isoformat(),
            'lastUpdatedAt': access_card.last_updated_at.isoformat(),
            'lastUpdatedByUserId': access_card.last_updated_by_user_id,
            'assignedTo': assigned_user,
            'assignmentLog': assignment_log
        }

        return jsonify(view=view)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')


# get access card assignment access logs
@app.route("/api/accessCards/<access_card_id>/logs", methods=["GET"])
@jwt_required()
def read_access_card_logs(access_card_id):
    if (not access_card_id):
        abort(422, 'missing access card id e.g. /api/accessCards/NODE-ID')

    try:
        # find
        access_card = AccessCard.query.filter_by(id=access_card_id).first()

        if not access_card:
            abort(404, 'unable to find a access card with that id')

        # TODO: create this as part of logs task, this may move to logs.py

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')


# assign access card to user
@app.route("/api/accessCards/<access_card_id>/assign", methods=["POST"])
@jwt_required()
def assign_access_card(access_card_id):
    role_required([UserRoleEnum.ADMIN])

    user_id = request.json.get("userId", None)

    if (not access_card_id):
        abort(
            422,
            'missing access card id e.g. /api/accessCards/CARD-ID/assign'
        )

    if (not user_id):
        abort(
            422,
            'missing user id'
        )

    try:
        # find access card that is also active
        access_card = AccessCard.query.filter_by(
            id=access_card_id,
            status=AccessCardStatusEnum.ACTIVE
        ).first()
        if not access_card:
            abort(404, 'unable to find an active access card with that id')

        # find user that is also active
        user = User.query.filter_by(
            id=user_id,
            status=UserStatusEnum.ACTIVE
        ).first()
        if not user:
            abort(404, 'unable to find a user with that id')

        # don't assign if already assigned
        user_access_card = UserAccessCard.query.filter_by(
            assigned_to_user_id=user_id,
            access_card_id=access_card_id
        ).first()
        if user_access_card:
            abort(409, 'card already assigned')

        # assign card to user
        user_access_card = UserAccessCard(
            assigned_to_user_id=user_id,
            access_card_id=access_card_id,
            assigned_by_user_id=current_user.id
        )
        db.session.add(user_access_card)
        db.session.commit()

        # log access card change
        access_card_log = AccessCardLog(
            access_card_id=access_card.id,
            assigned_to_user_id=user_access_card.assigned_to_user_id,
            assigned_by_user_id=user_access_card.assigned_by_user_id,
            status=access_card.status,
            emerge_access_level=user.emerge_access_level
        )
        db.session.add(access_card_log)
        db.session.commit()

        return jsonify(message='access card assigned')
    except exceptions.Conflict as err:
        abort(409, err)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')


# unassign access card to user
@app.route("/api/accessCards/<access_card_id>/unassign", methods=["DELETE"])
@jwt_required()
def unassign_access_card(access_card_id):
    role_required([UserRoleEnum.ADMIN])

    user_id = request.json.get("userId", None)

    if (not access_card_id):
        abort(
            422,
            'missing access card id e.g. /api/accessCards/CARD-ID/assign'
        )

    if (not user_id):
        abort(
            422,
            'missing user id'
        )

    try:
        # find access card assignment
        user_access_card = UserAccessCard.query.filter_by(
            access_card_id=access_card_id,
            assigned_to_user_id=user_id
        ).first()
        if not user_access_card:
            abort(404, 'unable to find an active access card assignment with \
                  that user id and access card id')

        # find access card
        access_card = AccessCard.query.filter_by(
            id=access_card_id,
        ).first()
        if not access_card:
            abort(404, 'unable to find an access card with that id')

        # find user
        user = User.query.filter_by(
            id=user_id
        ).first()
        if not user:
            abort(404, 'unable to find a user with that id')

        # unassign card from user
        db.session.delete(user_access_card)
        db.session.commit()

        # make card inactive (if active)
        if (access_card.status == AccessCardStatusEnum.ACTIVE):
            access_card.status = AccessCardStatusEnum.INACTIVE
            db.session.commit()

        # log access card change
        access_card_log = AccessCardLog(
            access_card_id=access_card.id,
            assigned_to_user_id=user_access_card.assigned_to_user_id,
            assigned_by_user_id=user_access_card.assigned_by_user_id,
            status=access_card.status,
            emerge_access_level=user.emerge_access_level
        )
        db.session.add(access_card_log)
        db.session.commit()

        return jsonify(message='access card unassigned')
    except exceptions.Conflict as err:
        abort(409, err)
    except exceptions.NotFound as err:
        abort(404, err)
    except Exception:
        abort(500, 'an unknown error occurred')
