from flask import Blueprint, jsonify

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register")
def register():
    return "Hello"