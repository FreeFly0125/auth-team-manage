from flask import Flask, request
from flask_cors import CORS
from database import db
import config

# Define API base route
BASE_ROUTE = "/bluquist/v" + config.VERSION

# Initialize flask app
app = Flask(__name__)
CORS(app)
app.config["MONGODB_SETTINGS"] = {
    "db" : "bluquist_" + config.ENVIRONMENT,
    "host" : config.MONGO
}
db.init_app(app)

# Import modules after app initialization to avoid circular references
from error import APIException, NotFoundError, MethodNotAllowedError
import auth
import util
import routes.static.route
import routes.user.route

# Register API routes
app.register_blueprint(routes.static.route.static, url_prefix=BASE_ROUTE + "/static")
app.register_blueprint(routes.user.route.user, url_prefix=BASE_ROUTE + "/user")

# Global request handlers
@app.errorhandler(APIException)
def handle_error(error):
    """Catches exceptions and builds a corresponding error response"""
    return error.getResponse()

@app.errorhandler(404)
def handle_404(error):
    return NotFoundError().getResponse()

@app.errorhandler(405)
def handle_405(error):
    return MethodNotAllowedError().getResponse()

@app.errorhandler(500)
def handle_500(error):
    return util.response(status_code=500, error_code=-1, error_message="The service encountered an unforeseen server error.")

@app.before_request
def handle_authentication():
    """Handles authentication for every non-public API request"""
    if request.endpoint is None or getattr(app.view_functions[request.endpoint], "is_public", False):
        return
    else:
        access_limit = getattr(app.view_functions[request.endpoint], "access_limit", None)
        auth.authenticate(access_limit)

@app.after_request
def save_session_state(r):
    """Saves the current session state after each request to the redis database"""
    auth.save_session()
    return r

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
