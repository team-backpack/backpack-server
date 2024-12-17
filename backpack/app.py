from flask import Flask, Blueprint
from backpack.middleware.protect_routes import ProtectRoutes
from backpack.routes import auth, users, posts, profiles, messages, communities
from flask_cors import CORS

app = Flask(__name__)
app.wsgi_app = ProtectRoutes(app.wsgi_app)
app.config.from_pyfile("../config.py")

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(auth.bp)
api.register_blueprint(users.bp)
api.register_blueprint(posts.bp)
api.register_blueprint(profiles.bp)
api.register_blueprint(messages.bp)
api.register_blueprint(communities.bp)

@api.route("/")
def index():
    return "Hello, world!"

app.register_blueprint(api)