from flask import Blueprint, request, jsonify
from backpack.models.community import Community, Participant
from backpack.utils import jwt
from backpack.utils import validation
from backpack.utils.constants import role_to_response

bp = Blueprint("communities", __name__, url_prefix="/communities")

@bp.route("/", methods=["GET", "POST"])
def communities():
    try:
        user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

        if request.method == "GET":
            participations = (
                Participant.select()
                .where(user_id=user_id)
                .order_by("since", descending=True)
                .execute()
            )

            response = []

            for participation in participations:
                response = Community.find_one(id=participation.community_id).to_dict()
                response["participation"] = participation.to_dict(show_profile=False)
            
            return jsonify(response), 200

        if request.method == "POST":
            data = request.get_json()

            name = data.get("name")
            display_name = data.get("displayName")
            description = data.get("description")
            banner_url = data.get("bannerURL")

            if not name:
                return jsonify({ "error": "Community name required" }), 400
            
            if not validation.is_name_valid(name):
                return jsonify({"error": "Invalid community name"}), 400
            
            community = Community(name=name, display_name=display_name, description=description, banner_url=banner_url)
            community.insert()

            admin = Participant(user_id=user_id, community_id=community.id, role="admin")
            admin.insert()

            response = community.to_dict()
            response["participants"] = { "administrators": [admin.user_id] }

            return jsonify(response), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/<string:community_id>/", methods=["GET", "PATCH", "DELETE"])
def community(community_id: str):
    try:
        if request.method == "GET":
            community = Community.find_one(id=community_id)
            if not community:
                return jsonify({ "error": "Community not found" }), 404

            return jsonify(community.to_dict(show_participants=True)), 200
        
        if request.method == "PATCH":
            data = request.get_json()

            display_name = data.get("displayName", None)
            description = data.get("description", None)
            banner_url = data.get("bannerURL", None)

            community = Community.find_one(id=community_id)
            if not community:
                return jsonify({ "error": "Community not found" }), 404
            
            community.display_name = display_name if display_name else community.display_name
            community.description = description if description else community.description
            community.banner_url = banner_url if banner_url else community.banner_url

            community.update()

            return jsonify(community.to_dict()), 200

        if request.method == "DELETE":
            community = Community.find_one(id=community_id)
            if not community:
                return jsonify({ "error": "Community not found" }), 404
            
            Community.delete(id=community_id)

            return jsonify({ "message": "Community deleted successfully" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/<string:community_id>/participants", methods=["GET", "POST", "DELETE"])
def participants(community_id: str):
    try:
        if request.method == "GET":
            limit = request.args.get("limit", default=None, type=int)
            offset = request.args.get("offset", default=None, type = int)

            if not Community.find_one(id=community_id):
                return jsonify({ "error": "Community not found" }), 404
            
            participants = Participant.find_all(community_id=community_id, limit=limit, offset=offset)

            response = { "administrators": [], "moderators": [], "members": [] }

            for participant in participants:
                obj = participant.to_dict()
                
                key = ""
                if participant.role in role_to_response.keys():
                    key = role_to_response[participant.role]

                response[key].append(obj)

            return jsonify(response), 200
        
        if request.method == "POST":
            if not Community.find_one(id=community_id):
                return jsonify({ "error": "Community not found" }), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            if Participant.find_one(community_id=community_id, user_id=user_id):
                return jsonify({ "error": "User already in community" }), 400
            
            participation = Participant(user_id=user_id, community_id=community_id)

            return jsonify(participation.to_dict(show_profile=False, show_user_id=True)), 201

        if request.method == "DELETE":
            if not Community.find_one(id=community_id):
                return jsonify({ "error": "Community not found" }), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            if not Participant.find_one(community_id=community_id, user_id=user_id):
                return jsonify({ "error": "User is not in community" }), 400

            if Participant.find_all(limit=2) == 1:
                Community.delete(id=community_id)
            
            Participant.delete(user_id=user_id, community_id=community_id)

            return jsonify({ "message": "Exited community successfully" }), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500