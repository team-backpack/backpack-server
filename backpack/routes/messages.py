from flask import Blueprint, request, jsonify
from backpack.models.message import Message
from backpack.utils import jwt

bp = Blueprint("messages", __name__, url_prefix="/messages")

@bp.route("/", methods=["GET"])
def messages():
    try:
        if request.method == "GET":
            messages = [message.to_dict() for message in Message.find_all()]
            return jsonify(messages), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500

@bp.route("/<string:receiver_id>/", methods=["GET", "POST"])
def conversation(receiver_id: str):
    try:
        if request.method == "GET":
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            conversation: list[Message] = Message.select().where(sender_id=user_id, receiver_id=receiver_id).order_by("createdAt").execute()
            messages = [message.to_dict() for message in conversation]
            
            return jsonify(messages), 200
        
        if request.method == "POST":
            data = request.get_json()

            text = data.get("text")
            if not text:
                return jsonify({ "error": "Cannot send message without content" }), 200

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            message = Message(sender_id=user_id, receiver_id=receiver_id, text=text)
            message.insert()
            
            return jsonify(message.to_dict()), 200
    
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500