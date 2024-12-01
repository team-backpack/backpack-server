from flask import request, jsonify, Response
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import JWT_SECRET
from backpack.models.user import User

JWT_EXPIRATION_IN_HOURS = 24
JWT_EXPIRATION_IN_SECONDS = JWT_EXPIRATION_IN_HOURS * 60 * 60

def generate_jwt(payload: dict, secret: str, expirates_in_hours: int):
    expiration = datetime.now() + timedelta(hours=expirates_in_hours)
    payload.update({ "exp": expiration })
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_jwt(token: str, secret: str):
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
def set_jwt_cookie(response: Response, user_id: str, username: str):
    payload = {
        "id": user_id,
        "username": username
    }
    token = generate_jwt(payload, JWT_SECRET, JWT_EXPIRATION_IN_HOURS)

    response.set_cookie("jwt", token, max_age=JWT_EXPIRATION_IN_SECONDS, httponly=True, secure=True)
    return response

def get_current_user_id(token: str):
    decoded_token = decode_jwt(token, JWT_SECRET)
    return decoded_token.get("id")

def jwt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get("jwt")

        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            decoded_token = decode_jwt(token, JWT_SECRET)

            if not decoded_token:
                return jsonify({"error": "Invalid token"}), 401
            
            user = User.find_one(id=decoded_token.get("id"))

            if not user:
                return jsonify({"error": "User not found"}), 404
            
            request.user = user
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return wrapped