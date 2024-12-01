from flask import Blueprint, request, jsonify
from backpack.models.post import Post
from backpack.models.user import User

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