from flask import Blueprint, request, jsonify
from backpack.utils.jwt import jwt_required
from backpack.models.user import User

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/", methods=["GET", "POST"])
@jwt_required
def users():

    if request.method == "GET":
        users = [user.to_dict() for user in User.find_all()]
        return jsonify(users), 200