from flask import Blueprint, request, jsonify, make_response
from datetime import date, datetime
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.utils import hashing
from backpack.utils import emailing
from backpack.utils import jwt
import re
import email_validator

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/logout/", methods=["POST"])
def logout():
    try:
        if request.method == "POST":
            response = make_response(jsonify({ "message": "Logged out successfully" }), 200)
            response.set_cookie("jwt", "")
            return response
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/login/", methods=["POST"])
def login():
    try:
        if request.method == "POST":
            data = request.get_json()

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not password or not (username or email):
                return jsonify({"error": "Missing fields"}), 400
            
            user = User.find_one(username=username) if username else User.find_one(email=email)

            if not user:
                return jsonify({"error": "User not found"}), 404
            
            is_password_correct = hashing.check(password, user.password)

            if not is_password_correct or not (user.username == username or user.email == email):
                return jsonify({"error": "Incorrect credentials"}), 401
            
            if not user.verified:
                return jsonify({"error": "User is not verified"}), 403

            response = make_response(jsonify({ "id": user.id }), 200)
            response = jwt.set_jwt_cookie(response, user.id, user.username)
            return response
    
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/register/", methods=["POST"])
def register():
    try:
        if request.method == "POST":
            data = request.get_json()
            
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            confirmed_password = data.get("confirmedPassword")
            birth_date = data.get("birthDate")

            if not all((username, email, password, confirmed_password, birth_date)):
                return jsonify({"error": "Missing fields"}), 400

            username_regex = re.compile(r'^[a-zA-Z0-9_.]+$')
            is_username_valid = bool(username_regex.match(username)) and (2 <= len(username) <= 20)
            if not is_username_valid:
                return jsonify({"error": "Invalid username"}), 400
            
            try:
                email_validator.validate_email(email)
            except email_validator.EmailNotValidError as e:
                return jsonify({"error": f"{e}"}), 400
            
            if password != confirmed_password:
                return jsonify({ "error": "Passwords do not match" }), 400
            
            user = User.find_one(username=username)
            if user:
                return jsonify({ "error": "Username already in use" }), 400
            
            user = User.find_one(email=email)
            if user:
                return jsonify({ "error": "Unavailable email" }), 400
            
            try:
                birth_date = date.fromisoformat(birth_date)
            except ValueError:
                return jsonify({"error": "Invalid birth date format"}), 400
            
            permited_age_in_days = 13 * 365
            if (date.today() - birth_date).days < permited_age_in_days:
                return jsonify({ "error": "User too young" }), 400
            
            password = hashing.hash(password)
            
            new_user = User(username=username, email=email, password=password, birth_date=birth_date)
            verification_token = new_user.generate_verification_token()

            new_user.insert()
            Profile(user_id=new_user.id).insert()

            emailing.send_verification_token(new_user.email, verification_token)
                
            response = make_response(jsonify({ "id": new_user.id }), 201)
            response = jwt.set_jwt_cookie(response, new_user.id, new_user.id)
            return response
            
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/verify/<string:user_id>/", methods=["POST"])
def verify(user_id: str):
    try:
        if request.method == "POST":
            verification_token = request.get_json().get("verificationToken")

            if not verification_token:
                return jsonify({"error": "Missing fields"}), 400

            user: User = User.find_one(id=user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            if user.verified:
                return jsonify({"error": "User is already verified"}), 400

            if user.verification_token != verification_token:
                return jsonify({ "error": "Invalid verification token" }), 400
            
            if is_verification_token_expired(user.token_sent_at):
                return jsonify({ "error": "Verification token expired" }), 400
            
            user.verified = True
            user.update()
            
            return jsonify({ "message": "User is now verified" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
        

@bp.route("/resend-token/<string:user_id>/", methods=["POST"])
def resend_token(user_id: str):
    try:
        if request.method == "POST":
            user: User = User.select().where(id=user_id).one()

            if user.verified:
                return jsonify({ "error": "User is already verified" }), 400
            
            verification_token = user.generate_verification_token()
            user.update()

            emailing.send_verification_token(user.email, verification_token)
            
            return jsonify({"message": "Token resent successfully"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


def is_verification_token_expired(token_sent_at: datetime):
    expiration_time_in_seconds = 5 * 60
    return (datetime.now() - token_sent_at).total_seconds() > expiration_time_in_seconds
