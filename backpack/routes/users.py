from flask import Blueprint, request, jsonify
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.models.follow import Follow
from backpack.models.message import Message
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
    

@bp.route("/<string:participant_id>/messages/", methods=["GET", "POST"])
def messages(participant_id: str):
    try:
        if request.method == "GET":
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            conversation: list[Message] = ( 
                Message.select()
                .where(sender_id=user_id, receiver_id=participant_id)
                .or_where(sender_id=participant_id, receiver_id=user_id)
                .order_by("created_at", descending=True)
                .execute()
            )
            messages = [message.to_dict(show_participants_id=True) for message in conversation]
            
            return jsonify(messages), 200
        
        if request.method == "POST":
            data = request.get_json()

            text = data.get("text")
            if not text:
                return jsonify({ "error": "Cannot send message without content" }), 200

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            message = Message(sender_id=user_id, receiver_id=participant_id, text=text)
            message.insert()
            
            return jsonify(message.to_dict()), 201
    
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500