from flask import request, jsonify, Response
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import JWT_SECRET
from backpack.models.user import User

JWT_EXPIRATION_IN_HOURS = 2

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

    response.headers["Authorization"] = f"Bearer {token}"
    return response

def jwt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token is missing"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded_token = decode_jwt(token, JWT_SECRET)
            if not decoded_token:
                return jsonify({"error": "Invalid token"}), 401
            
            user = User.find_one(id=decoded_token.get("id"))
            if not user:
                return jsonify({"error": "User not found"}), 404
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return wrapped