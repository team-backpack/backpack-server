from flask import Flask, Blueprint
from backpack.routes import auth

app = Flask(__name__)

api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(auth.bp)

@api.route("/")
def index():
    return "Hello, world!"

app.register_blueprint(api)