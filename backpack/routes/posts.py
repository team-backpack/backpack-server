from flask import Blueprint, request, jsonify
from datetime import datetime
from backpack.models.post.post import Post
from backpack.models.post.media import Media
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
            media_urls = data.get("mediaURLs")

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            new_post = Post(user_id=user_id, text=text)
            new_post.insert()

            for media_url in media_urls:
                Media(url=media_url, post_id=new_post.id).insert()

            response = new_post.to_dict()

            return jsonify(response), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500


@bp.route("/<string:post_id>/", methods=["GET", "PATCH", "DELETE"])
def post(post_id: str):
    try:
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

            if post.commented_id:
                commented = Post.find_one(id=post.commented_id)
                commented.comments -= 1
                commented.update()

            if post.reposted_id:
                reposted = Post.find_one(id=post_id)
                reposted.reposts -= 1
                reposted.update()

            return jsonify({ "message": "Post deleted successfully" }), 200
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
    

@bp.route("/<string:post_id>/likes/", methods=["GET", "POST", "DELETE"])
def like(post_id: str):
    try:
        if request.method == "GET":
            likes: list[Like] = Like.find_all(post_id=post_id)

            response = []

            for like in likes:
                profile = Profile.find_one(user_id=like.user_id)
                if profile:
                    response.append(profile.to_dict())

            return jsonify(response), 200
            
        if request.method == "POST":
            post = Post.find_one(id=post_id)

            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            like = Like.find_one(user_id=user_id, post_id=post_id)
            if like:
                return jsonify({ "message": "Post already liked" }), 400

            Like(user_id=user_id, post_id=post_id).insert()

            post.likes += 1
            post.update()

            return jsonify({ "message": "Post liked successfully" }), 200
            
        if request.method == "DELETE":
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
    try:
        if request.method == "GET":
            reposts: list[Post] = Post.find_all(reposted_id=post_id, is_repost=True)

            response = [repost.to_dict() for repost in reposts]
            return jsonify(response), 200
        

        if request.method == "POST":
            data = request.get_json()

            text = data.get("text", None)
            media_urls = data.get("mediaURLs", None)

            reposted = Post.find_one(id=post_id)
            if not reposted:
                return jsonify({"error": "Reposted post not found"}), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            repost = Post.find_one(user_id=user_id, reposted_id=reposted.id, is_repost=True)
            if repost:
                return jsonify({"error": "Cannot repost the same post 2 or more times"}), 400

            repost = Post(user_id=user_id, text=text, is_repost=True, reposted_id=reposted.id)
            repost.insert()

            for media_url in media_urls:
                Media(url=media_url, post_id=repost.id).insert()

            reposted.reposts += 1
            reposted.update()

            return jsonify(repost.to_dict()), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500
        

@bp.route("/<string:post_id>/comments/", methods=["GET", "POST", "DELETE"])
def comments(post_id: str):
    try:
        if request.method == "GET":
            comments: list[Post] = Post.find_all(commented_id=post_id)

            response = [comment.to_dict() for comment in comments]

            return jsonify(response), 200

        if request.method == "POST":
            data = request.get_json()

            text = data.get("text")
            media_urls = data.get("mediaURLs", "")

            commented = Post.find_one(id=post_id)
            if not commented:
                return jsonify({"error": "Commented post not found"}), 404
            
            user_id = jwt.get_current_user_id(request.cookies.get("jwt"))

            comment = Post(user_id=user_id, text=text, commented_id=commented.id)
            comment.insert()

            for media_url in media_urls:
                Media(url=media_url, post_id=comment.id).insert()

            commented.comments += 1
            commented.update()

            return jsonify(comment.to_dict()), 201
        
    except Exception as e:
        print(e)
        return jsonify({ "error": "Internal Server Error" }), 500