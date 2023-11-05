#TODO protect endpoints based on user roles
#TODO filter by node
#TODO filter by user access
#TODO get one machine
#TODO pagination
#TODO sort
#TODO: api error handling that doesn't return an HTML page, json would be nicer at least

from ..models import Device
from ..models import DeviceTypeEnum
from .. import db
from .. import app
from datetime import datetime
from datetime import timezone
from flask import jsonify
from flask import Blueprint
from flask import request
from flask import abort
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import current_user
import jwt
from json import dumps
from sqlalchemy import exc

devices = Blueprint('devices', __name__)

@app.route("/api/devices", methods=["POST"])
@jwt_required()
def create_device():
    type = request.json.get("type", None).strip()
    name = request.json.get("name", None).strip()

    if (not type or not name):
        abort(422, 'missing type or name')

    valid_type = type in [e.value for e in DeviceTypeEnum]
    if (not valid_type):
        abort(422, 'invalid type')
    
    try:
        # create
        device = Device(type=type, name=name)
        db.session.add(device)
        db.session.commit()
        
        # get full data
        db.session.refresh(device)

        return jsonify(id=device.id, name=device.name, type=device.type, created_at=device.created_at.isoformat())
    except exc.IntegrityError:
        abort(409, 'a device with that name already exists')
    except Exception as err:
        abort(403, 'an unknown error occurred')