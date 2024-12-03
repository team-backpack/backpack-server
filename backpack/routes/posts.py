from flask import Blueprint, request, jsonify
from datetime import datetime
from backpack.models.post import Post
from backpack.models.user import User
from backpack.models.like import Like
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


@bp.route("/<string:post_id>", methods=["GET", "PATCH", "DELETE"])
def post(post_id: str):

    if request.method == "GET":
        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        return jsonify(post.to_dict()), 200
    
    if request.method == "PATCH":
        data = request.get_json()

        text = data.get("text")

        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        post.text = text
        post.was_edited_at = datetime.now()
        post.update()

        return jsonify(post.to_dict()), 200
    
    if request.method == "DELETE":
        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        Post.delete(id=post_id)

        return jsonify({ "message": "Post deleted successfully" }), 200
    

@bp.route("/<string:post_id>/like/", methods=["POST"])
def like(post_id: str):
        
    if request.method == "POST":

        try:
            post = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))
            user = User.find_one(id=user_id)

            like = Like.find_one(user=user, post=post)
            if like:
                return jsonify({ "message": "Post already liked" }), 400

            Like(user=user, post=post).insert()

            post.likes += 1
            post.update()

            return jsonify({ "message": "Post liked successfully" }), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500