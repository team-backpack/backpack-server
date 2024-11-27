from flask import Blueprint, request, jsonify
from datetime import date, datetime
from backpack.models.user import User
from backpack.utils.hashing import hash, check
from backpack.utils.emailing import send_verification_token_to_email
from backpack.utils.jwt import generate_jwt, JWT_EXPIRATION_IN_HOURS
from config import JWT_SECRET

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register/", methods=["POST"])
def register():
    
    if request.method == "POST":
        data = request.get_json()
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirmed_password = data.get("confirmedPassword")
        birth_date = data.get("birthDate")

        if not all((username, email, password, confirmed_password, birth_date)):
            return jsonify({"error": "Missing fields"}), 400

        try:
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
            
            password = hash(password)
            
            new_user = User(username=username, email=email, password=password, birth_date=birth_date)
            verification_token = new_user.generate_verification_token()

            new_user.insert()

            send_verification_token_to_email(new_user.email, verification_token)
                
            payload = {
                "id": new_user.id,
                "username": new_user.username
            }
            token = generate_jwt(payload, JWT_SECRET, JWT_EXPIRATION_IN_HOURS)
            
            return jsonify({ "id": new_user.id, "token": token }), 201
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/verify/", methods=["POST"])
def verify():

    if request.method == "POST":
        id = request.get_json().get("id")
        verification_token = request.get_json().get("verificationToken")

        if not all((id, verification_token)):
            return jsonify({"error": "Missing fields"}), 400

        try:
            user: User = User.select().where(id=id).one()
            if user.verification_token != verification_token:
                return jsonify({ "error": "Invalid token" }), 400
            
            if is_verification_token_expired(user.token_sent_at):
                return jsonify({ "error": "Expired token" }), 400
            
            user.verified = True
            user.update()
            
            return jsonify({}), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        

@bp.route("/resend-token/", methods=["POST"])
def resend_token():

    if request.method == "POST":
        id = request.get_json().get("id")

        if not all(id):
            return jsonify({"error": "Missing fields"}), 400

        try:
            user: User = User.select().where(id=id).one()

            if user.verified:
                return jsonify({ "error": "User is already verified" }), 400
            
            verification_token = user.generate_verification_token()
            user.update()

            send_verification_token_to_email(user.email, verification_token)
            
            return 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500

def is_verification_token_expired(token_sent_at: datetime):
    expiration_time_in_seconds = 5 * 60
    return (datetime.now() - token_sent_at).total_seconds() > expiration_time_in_seconds
