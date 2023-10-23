from flask import Blueprint

hello = Blueprint('hello', __name__)

@hello.route('/api/hello')
def index():
    data = {
        'message': 'hello!'
    }
    return data