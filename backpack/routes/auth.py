from flask import Blueprint, request, jsonify
import bcrypt
from datetime import date
from backpack.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["POST"])
def register():
    
    if request.method == "POST":
        username = request.get_json().get("username")
        email = request.get_json().get("email")
        password = request.get_json().get("password")
        confirmed_password = request.get_json().get("confirmedPassword")
        birth_date = request.get_json().get("birthDate")

        try:
            if password != confirmed_password:
                return jsonify({ "error": "Passwords do not match" }), 400
            
            user = User.find_one(username=username, email=email)
            if user:
                return jsonify({ "error": "Username already in use" }), 400
            
            password = hash(password)
            birth_date = date.fromisoformat(birth_date)
            
            new_user = User(username=username, email=email, password=password, birth_date=birth_date)

            new_user.insert()
            
            return jsonify({ "id": new_user.id }), 201
        except:
            return jsonify({ "error": "Internal Server Error" }), 500
        
def hash(senha: str):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def check(senha: str, hashed: str):
    return bcrypt.checkpw(senha.encode(), hashed.encode())