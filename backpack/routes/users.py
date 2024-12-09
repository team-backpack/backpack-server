from flask import Blueprint, request, jsonify
from backpack.models.user import User

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/", methods=["GET", "POST"])
def users():
    try:
        if request.method == "GET":
            users = [user.to_dict() for user in User.find_all()]
            return jsonify(users), 200
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500