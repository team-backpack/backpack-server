from flask import Blueprint, request, jsonify
from backpack.models.message import Message
from backpack.models.profile.profile import Profile
from backpack.models.user import User
from backpack.utils import jwt
from datetime import datetime

bp = Blueprint("messages", __name__, url_prefix="/messages")

@bp.route("/", methods=["GET"])
def messages():
    try:
        if request.method == "GET":
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            messages: list[Message] = (
                Message.select()
                .where(operator="OR", sender_id=user_id, receiver_id=user_id)
                .order_by("created_at", descending=True)
                .execute()
            )

            conversations = {}

            for message in messages:
                other_id = message.sender_id if message.sender_id != user_id else message.receiver_id

                if other_id not in conversations:
                    profile = Profile.find_one(user_id=other_id)
                    conversations[other_id] = {
                        "participant": profile.to_dict() if profile else User.find_one(id=other_id).to_dict(),
                        "lastMessage": None,
                    }
        
                conversations[other_id]["lastMessage"] = message.to_dict(show_participants_id=True)

            response = sorted(list(conversations.values()), key=lambda c: c["lastMessage"]["createdAt"], reverse=True)

            return jsonify(response), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/<string:message_id>/", methods=["GET", "PATCH", "DELETE"])
def message(message_id: str):
    try:
        if request.method == "GET":
            message = Message.find_one(id=message_id)
            if not message:
                return jsonify({ "error": "Message not found" }), 404
            
            return jsonify(message.to_dict(show_participants_id=True)), 200

        if request.method == "PATCH":
            data = request.get_json()
            
            text = data.get("text")

            message = Message.find_one(id=message_id)
            if not message:
                return jsonify({ "error": "Message not found" }), 404
            
            message.text = text
            message.was_edited_at = datetime.now()
            
            return jsonify(message.to_dict(show_participants_id=True)), 200

        if request.method == "DELETE":
            message = Message.find_one(id=message_id)

            if not message:
                return jsonify({ "error": "Message not found" }), 404
            
            Message.delete(id=message_id)

            return jsonify({ "message": "Message deleted successfully" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/read/", methods=["PATCH"])
def read():
    try:
        if request.method == "PATCH":
            data = request.get_json()
            
            messages = data.get("messages")

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            for message_id in messages:
                message = Message.find_one(id=message_id)

                if not message:
                    return jsonify({ "error": "Message not found" }), 404
                
                if message.sender_id == user_id:
                    continue
                
                Message.patch(id=message_id, seen=True)
            
            return jsonify({ "message": "Messages read successfully" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500