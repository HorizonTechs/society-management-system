from flask import request, jsonify, current_app
import jwt
from functools import wraps
import requests

from ..models import User

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"]

        if not token:
            return jsonify(message="Login required"), 401

        try:
            data = jwt.decode(token.split("Bearer ")[1], current_app.config["SECRET_KEY"])
            current_user = User.query.filter_by(uuid = data["uuid"]).first()
            if not current_user: raise
        except:
            return jsonify(message="Invalid username or password"), 401
        return f(current_user, *args, **kwargs)

    return decorated

def validate_captcha(token):
    secret = current_app.config["CAPTCHA_SECRET_KEY"]
    response = requests.post(f"https://www.google.com/recaptcha/api/siteverify?secret={secret}&response={token}")
    if response and response.json()['success']:
        return True
    return False