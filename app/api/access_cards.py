from ..models import AccessCard
from ..model_enums import AccessCardStatusEnum, UserRoleEnum
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
from datetime import datetime
from datetime import timezone
from werkzeug import exceptions

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
        abort(422, 'missing device id e.g. /api/accessCards/NODE-ID')

    if (not card_number):
        abort(422, 'missing cardNumber')

    # validate optional status if assigned
    if (status):
        valid_status = status in [e.value for e in AccessCardStatusEnum]
        if (not valid_status):
            abort(422, 'invalid status')

    try:
        # find
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


# TODO: Consider removing references from other tables once those exist
# archive an access card
@app.route("/api/accessCards/<access_card_id>", methods=["DELETE"])
@jwt_required()
def archive_access_card(access_card_id):
    role_required([UserRoleEnum.ADMIN])

    if (not access_card_id):
        abort(422, 'missing access card id e.g. /api/accessCards/CARD-ID')

    try:
        # find
        access_card = AccessCard.query.filter_by(id=access_card_id).first()

        if not access_card:
            abort(404, 'unable to find a device with that id')

        # archive access card
        access_card.status = AccessCardStatusEnum.ARCHIVED
        db.session.commit()

        # TODO: clear any device assignments to node

        return jsonify(message='access card archived')
    except exceptions.NotFound:
        abort(404, 'unable to find an access card with that id')
    except Exception:
        abort(500, 'an unknown error occurred')


# return a list of access cards
@app.route("/api/accessCards", methods=["GET"])
@jwt_required()
def read_access_cards():
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

    query = AccessCard.query

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
        access_cards.append({
            'id': access_card.id,
            'cardNumber': access_card.card_number,
            'facilityCode': access_card.facility_code,
            'cardType': access_card.card_type,
            'status': access_card.status,
            'createdAt': access_card.created_at.isoformat(),
            'lastUpdatedAt': access_card.last_updated_at.isoformat(),
            'lastUpdatedByUserId': access_card.last_updated_by_user_id
        })

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
        access_card = AccessCard.query.filter_by(id=access_card_id).first()

        if not access_card:
            abort(404, 'unable to find a device with that id')

        view = {
            'id': access_card.id,
            'cardNumber': access_card.card_number,
            'facilityCode': access_card.facility_code,
            'cardType': access_card.card_type,
            'status': access_card.status,
            'createdAt': access_card.created_at.isoformat(),
            'lastUpdatedAt': access_card.last_updated_at.isoformat(),
            'lastUpdatedByUserId': access_card.last_updated_by_user_id,
            'assignedTo': {
                'id': 'soon',
                'more': 'soon',
            },
            'assignmentHistory': [
                {
                    'id': 'soon',
                    'more': 'soon'
                }
            ]
        }

        return jsonify(view=view)
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

        # TODO: finish this one after assignments are working

        return jsonify(logs='TODO')
    except Exception:
        abort(500, 'an unknown error occurred')
