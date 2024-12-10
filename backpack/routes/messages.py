from flask import Blueprint, request, jsonify
from backpack.models.message import Message
from backpack.models.profile.profile import Profile
from backpack.models.user import User
from backpack.utils import jwt

bp = Blueprint("messages", __name__, url_prefix="/messages")

@bp.route("/", methods=["GET"])
def conversations():
    try:
        if request.method == "GET":
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            messages: list[Message] = (
                Message.select()
                .where(operator="OR", sender_id=user_id, receiver_id=user_id)
                .order_by("createdAt")
                .execute()
            )

            conversations = {}

            for message in messages:
                other_id = message.sender_id if message.sender_id != user_id else message.receiver_id

                if other_id not in conversations:
                    profile = Profile.find_one(id=other_id)
                    conversations[other_id] = {
                        "participant": profile.to_dict() if profile else User.find_one(id=other_id).to_dict(),
                        "messages": [],
                    }
        
                conversations[other_id]["messages"].append(message.to_dict(show_participants_id=True))

            return jsonify(list(conversations.values())), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500

@bp.route("/<string:participant_id>/", methods=["GET", "POST"])
def conversation(participant_id: str):
    try:
        if request.method == "GET":
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            conversation: list[Message] = Message.select().where(sender_id=user_id, receiver_id=participant_id).order_by("createdAt").execute()
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
            
            return jsonify(message.to_dict()), 200
    
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500