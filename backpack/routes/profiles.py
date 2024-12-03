from flask import Blueprint, request, jsonify
from backpack.models.profile.profile import Profile
from backpack.models.profile.location import Location, Country, Region, City
from backpack.models.profile.cultural_interest import CulturalInterest, ProfileCulturalInterest
from backpack.models.profile.general_interest import GeneralInterest, ProfileGeneralInterest
from backpack.models.profile.language import Language
from backpack.models.user import User
from backpack.models.post import Post
from backpack.utils import jwt

bp = Blueprint("profiles", __name__, url_prefix="/profiles")

@bp.route("/", methods=["POST"])
def profiles():

    if request.method == "POST":
        data = request.get_json()

        display_name = data.get("displayName")
        description = data.get("description")
        picture_url = data.get("pictureURL")
        banner_url = data.get("bannerURL")
        location = data.get("location")
        language = data.get("language")
        cultural_interests = data.get("culturalInterests")
        general_interests = data.get("generalInterests")

        if not all((display_name, description, picture_url, banner_url)):
            return jsonify({"error": "Missing fields"}), 400

        try:
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            profile = Profile(
                user=User.find_one(id=user_id), 
                display_name=display_name,
                description=description,
                picture_url=picture_url,
                banner_url=banner_url
            )

            location = Location.find_one(
                country=Country.find_one(name=location.get("country")), 
                region=Region.find_one(name=location.get("region")), 
                city=City.find_one(name=location.get("city"))
            )
            profile.location = location

            profile.language = Language.find_one(code=language)

            profile.insert()

            result = profile.to_dict()

            result["culturalInterests"] = []
            for name in cultural_interests:
                cultural_interest = CulturalInterest.find_one(name=name)

                if cultural_interest:
                    ProfileCulturalInterest(profile=profile, cultural_interest=cultural_interest).insert()

                    result["culturalInterests"].append(cultural_interest)
                
            result["generalInterests"] = []
            for name in general_interests:
                general_interest = GeneralInterest.find_one(name=name)

                if general_interest:
                    ProfileGeneralInterest(profile=profile, general_interest=general_interest).insert()

                    result["generalInterests"].append(general_interest)

            return jsonify(result), 201

        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/<string:username>", methods=["GET"])
def profile(username: str):

    if request.method == "GET":

        try:
            user = User.find_one(username=username)

            profile = Profile.find_one(user=user)
            posts = Post.find_all(user=user)

            result = profile.to_dict()

            result["culturalInterests"] = [
                profile_cultural_interest.cultural_interest for profile_cultural_interest in ProfileCulturalInterest.find_all(profile=profile)
            ]

            result["posts"] = [post.to_dict(show_user=False) for post in posts]

            return jsonify(result), 200

        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500