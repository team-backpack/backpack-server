from flask import Blueprint, request, jsonify
from backpack.models.post import Post
from backpack.models.user import User
from backpack.utils import jwt

bp = Blueprint("posts", __name__, url_prefix="/posts")

@bp.route("/", methods=["GET", "POST"])
def users():

    if request.method == "GET":
        posts = Post.find_all()

        all_posts = []

        for post in posts:
            json = post.to_dict()
            json["user"] = post.user.to_dict()

            all_posts.append(json)
        
        return jsonify(all_posts), 200
    
    if request.method == "POST":
        data = request.get_json()

        text = data.get("text")
        content_url = data.get("contentURL")
        is_shared_post = data.get("isSharedPost")

        user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

        new_post = Post(user=User.find_one(id=user_id), text=text, content_url=content_url, is_shared_post=is_shared_post)
        new_post.insert()

        return jsonify(new_post.to_dict()), 201