from json import dumps
from backpack.utils import jwt
from config import JWT_SECRET
from backpack.models.user import User


class ProtectRoutes():
    def __init__(self, app):
        self.app = app
        self.excluded_routes = ["/api/auth/login/", "/api/auth/register/", "/api/auth/resend-token/"]

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")

        if path in self.excluded_routes:
            return self.app(environ, start_response)

        token = environ.get("HTTP_COOKIE")
        token = token.split("=")[1]

        if not token:
            return self._respond(start_response, "Token is missing")
        
        try:
            decoded_token = jwt.decode_jwt(token, JWT_SECRET)

            if not decoded_token:
                return self._respond(start_response, "Invalid token")
            
            user = User.find_one(id=decoded_token.get("id"))

            if not user:
                return self._respond(start_response, "User not found", status="404 Not Found")
            
        except ValueError as e:
            return self._respond(start_response, str(e))

        return self.app(environ, start_response)
    
    def _respond(self, start_response, message, status: str = "401 Unauthorized"):
        body = dumps({"error": message}).encode("UTF-8")
        status = status
        headers = [("Content-Type", "application/json")]
        start_response(status, headers)
        return [body]