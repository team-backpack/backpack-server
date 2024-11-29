from flask import Flask, Blueprint
from backpack.middleware.protect_routes import ProtectRoutes
from backpack.routes import auth, users

app = Flask(__name__)
app.wsgi_app = ProtectRoutes(app.wsgi_app)

api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(auth.bp)
api.register_blueprint(users.bp)

@api.route("/")
def index():
    return "Hello, world!"

app.register_blueprint(api)