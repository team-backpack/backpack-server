from flask import Blueprint, request, jsonify
from datetime import datetime
from backpack.models.post import Post
from backpack.models.user import User
from backpack.models.profile.profile import Profile
from backpack.models.interaction.like import Like
from backpack.models.interaction.repost import Repost
from backpack.utils import jwt

bp = Blueprint("posts", __name__, url_prefix="/posts")

@bp.route("/", methods=["GET", "POST"])
def posts():

    if request.method == "GET":
        posts = [post for post in Post.find_all()]

        response = []

        for post in posts:
            result = post.to_dict()
            result["profile"] = Profile.find_one(user=post.user).to_dict(show_user=False)
            response.append(result)

        return jsonify(response), 200
    
    if request.method == "POST":
        data = request.get_json()

        text = data.get("text")
        media_url = data.get("mediaURL")
        is_shared_post = data.get("isSharedPost")

        user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

        new_post = Post(user=User.find_one(id=user_id), text=text, media_url=media_url, is_shared_post=is_shared_post)
        new_post.insert()

        return jsonify(new_post.to_dict()), 201


@bp.route("/<string:post_id>", methods=["GET", "PATCH", "DELETE"])
def post(post_id: str):

    if request.method == "GET":
        post = Post.find_one(id=post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        response = post.to_dict()
        response["profile"] = Profile.find_one(user=post.user).to_dict(show_user=False)

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
            likes: list[Like] = Like.find_all(post=Post.find_one(id=post_id))

            response = []

            for like in likes:
                profile = Profile.find_one(user=like.user)
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
        
    if request.method == "DELETE":

        try:
            post = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))
            user = User.find_one(id=user_id)

            like = Like.find_one(user=user, post=post)
            if not like:
                return jsonify({ "message": "Post is not liked" }), 400

            Like.delete(user=user, post=post)

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
            reposts: list[Repost] = Repost.find_all(reposted=Post.find_one(id=post_id))

            response = []

            for repost in reposts:
                result = {}

                result["post"] = None if not repost.post else repost.post.to_dict()

                profile = Profile.find_one(user=repost.user)
                if profile:
                    result["profile"] = profile.to_dict()

                response.append(result)

            return jsonify(response), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500

    if request.method == "POST":
        data = request.get_json()

        text = data.get("text")
        media_url = data.get("mediaURL", "")
        is_shared_post = data.get("isSharedPost", False)

        try:
            reposted = Post.find_one(id=post_id)
            if not reposted:
                return jsonify({"error": "Reposted post not found"}), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))
            user = User.find_one(id=user_id)

            repost = Repost.find_one(user=user, reposted=reposted)
            if repost:
                return jsonify({"error": "Cannot repost the same post 2 or more times"}), 400

            if not text and not media_url:
                repost = Repost(user=user,reposted=reposted)
            else:
                user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

                post = Post(user=user, text=text, media_url=media_url, is_shared_post=is_shared_post)
                post.insert()

                repost = Repost(user=user, post=post, reposted=reposted)
                
            repost.insert()

            reposted.reposts += 1
            reposted.update()

            return jsonify(repost.to_dict(show_user=False)), 201
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500
        
    if request.method == "DELETE":
        try:
            reposted = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))
            user = User.find_one(id=user_id)

            repost = Repost.find_one(user=user, reposted=reposted)

            if not repost:
                jsonify({ "error": "Repost not found" }), 404

            Repost.delete(id=repost.id)
            Post.delete(id=repost.post.id)

            reposted.reposts -= 1
            reposted.update()

            return jsonify({ "message": "Repost deleted successfully" }), 200
        except Exception as e:
            print(e)
            return jsonify({ "error": "Internal Server Error" }), 500