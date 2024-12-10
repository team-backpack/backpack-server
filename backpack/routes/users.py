from flask import Blueprint, request, jsonify
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.models.follow import Follow
from backpack.utils import jwt

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
    

@bp.route("/<string:following_id>/follow/", methods=["POST"])
def follow(following_id: str):
    try:        
        if request.method == "POST":
            follower_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            Follow(follower_id=follower_id, following_id=following_id).insert()
            return jsonify({ "message": "Now following" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/<string:user_id>/followers/", methods=["GET"])
def followers(user_id: str):
    try:        
        if request.method == "GET":
            followers = [Profile.find_one(user_id=follow.follower_id).to_dict() for follow in Follow.find_all(following_id=user_id)]
            return jsonify(followers), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/<string:user_id>/following/", methods=["GET"])
def following(user_id: str):
    try:        
        if request.method == "GET":
            followers = [Profile.find_one(user_id=follow.following_id).to_dict() for follow in Follow.find_all(follower_id=user_id)]
            return jsonify(followers), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500