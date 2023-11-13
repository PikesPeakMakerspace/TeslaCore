from flask import Blueprint

health = Blueprint('health', __name__)


@health.route('/api/health')
def index():
    data = {
        'message': 'alive'
    }
    return data
