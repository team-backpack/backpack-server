from flask import Blueprint, request, jsonify
from datetime import datetime
from backpack.models.post.post import Post
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.models.post.like import Like
from backpack.utils import jwt

bp = Blueprint("posts", __name__, url_prefix="/posts")

@bp.route("/", methods=["GET", "POST"])
def posts():
    try:
        if request.method == "GET":
            posts = [post.to_dict() for post in Post.find_all()]
            return jsonify(posts), 200
    
        if request.method == "POST":
            data = request.get_json()

            text = data.get("text")
            media_url = data.get("mediaURL")

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            new_post = Post(user_id=user_id, text=text, media_url=media_url)
            new_post.insert()

            response = new_post.to_dict()

            return jsonify(response), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/<string:post_id>/", methods=["GET", "PATCH", "DELETE"])
def post(post_id: str):

    if request.method == "GET":
        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        response = post.to_dict()

        return jsonify(response), 200
    
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
    

@bp.route("/<string:post_id>/likes/", methods=["GET", "POST", "DELETE"])
def like(post_id: str):

    if request.method == "GET":
        try:
            likes: list[Like] = Like.find_all(post_id=post_id)

            response = []

            for like in likes:
                profile = Profile.find_one(user_id=like.user_id)
                if profile:
                    response.append(profile.to_dict())

            return jsonify(response), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        
    if request.method == "POST":

        try:
            post = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            like = Like.find_one(user_id=user_id, post_id=post_id)
            if like:
                return jsonify({ "message": "Post already liked" }), 400

            Like(user_id=user_id, post_id=post_id).insert()

            post.likes += 1
            post.update()

            return jsonify({ "message": "Post liked successfully" }), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        
    if request.method == "DELETE":

        try:
            post = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            like = Like.find_one(user_id=user_id, post_id=post_id)
            if not like:
                return jsonify({ "message": "Post is not liked" }), 400

            Like.delete(user_id=user_id, post_id=post_id)

            post.likes -= 1
            post.update()

            return jsonify({ "message": "Post disliked successfully" }), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        

@bp.route("/<string:post_id>/reposts/", methods=["GET", "POST", "DELETE"])
def reposts(post_id: str):

    if request.method == "GET":
        try:
            reposts: list[Post] = Post.find_all(reposted_id=post_id, is_repost=True)

            response = [repost.to_dict() for repost in reposts]

            return jsonify(response), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500

    if request.method == "POST":
        data = request.get_json()

        text = data.get("text")
        media_url = data.get("mediaURL", "")

        try:
            reposted = Post.find_one(id=post_id)
            if not reposted:
                return jsonify({"error": "Reposted post not found"}), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            repost = Post.find_one(user_id=user_id, reposted_id=reposted.id, is_repost=True)
            if repost:
                return jsonify({"error": "Cannot repost the same post 2 or more times"}), 400

            if not text and not media_url:
                repost = Post(user_id=user_id, is_repost=True, reposted_id=reposted.id)
            else:
                repost = Post(user_id=user_id, text=text, media_url=media_url, is_repost=True, reposted_id=reposted.id)
                repost.insert()
                
            repost.insert()

            reposted.reposts += 1
            reposted.update()

            return jsonify(repost.to_dict()), 201
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        
    if request.method == "DELETE":
        try:
            reposted = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))
            user = User.find_one(id=user_id)

            repost = Post.find_one(user_id=user_id, reposted_id=reposted.id, is_repost=True)

            if not repost:
                jsonify({ "error": "Repost not found" }), 404

            Post.delete(id=repost.id)

            reposted.reposts -= 1
            reposted.update()

            return jsonify({ "message": "Repost deleted successfully" }), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500