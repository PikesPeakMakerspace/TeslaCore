from flask import Blueprint, render_template, redirect, url_for, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from flask_login import login_user, login_required, logout_user, current_user

api_auth = Blueprint('api_auth', __name__)

@api_auth.route('/api/auth/login', methods=['POST'])
def login_post():
    json = request.json
    email = json['email']
    password = json['password']

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return make_response('Unauthorized', 401)
    
    login_user(user, remember=True)

    return { 'token': current_user.name }

@api_auth.route('/api/auth/logout')
@login_required
def logout():
    logout_user()
    return { 'message': 'ok' }