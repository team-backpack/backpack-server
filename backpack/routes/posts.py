from flask import Blueprint, request, jsonify
from datetime import datetime
from backpack.models.post import Post
from backpack.models.user import User
from backpack.utils import jwt

bp = Blueprint("posts", __name__, url_prefix="/posts")

@bp.route("/", methods=["GET", "POST"])
def posts():

    if request.method == "GET":
        posts = [post.to_dict() for post in Post.find_all()]
        return jsonify(posts), 200
    
    if request.method == "POST":
        data = request.get_json()

        text = data.get("text")
        content_url = data.get("contentURL")
        is_shared_post = data.get("isSharedPost")

        user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

        new_post = Post(user=User.find_one(id=user_id), text=text, content_url=content_url, is_shared_post=is_shared_post)
        new_post.insert()

        return jsonify(new_post.to_dict()), 201


@bp.route("/<string:post_id>", methods=["GET", "PUT", "DELETE"])
def post(post_id: str):

    if request.method == "GET":
        return jsonify(Post.find_one(id=post_id).to_dict()), 200
    
    if request.method == "PUT":
        data = request.get_json()

        text = data.get("text")

        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        post.text = text
        post.was_edited_at = datetime.now()
        post.update()

        return jsonify(post.to_dict()), 200