"""Request authentication

This module provides methods and decorators to handle authentication of
requests.
"""

from flask import request, g
import time
import uuid
import hashlib
import base64
from functools import wraps
from RedisAdapter import RedisAdapter
from error import APIException, InvalidRequestHeader
from model.User import User, UserRole

from util import get_request_ip

_public_paths = []

def _get_request_ip():
    return get_request_ip()

def start_session(user_id, user_role):
    """Starts a new session for the given user ID"""
    token = uuid.uuid4()
    session = {
        "userID" : user_id,
        "userRole" : user_role,
        "clientIP" : _get_request_ip(),
        # New sessions will expire after 30 minutes of inactivity
        "expireDate" : time.time() + (60 * 30),
        "sessionToken" : token
    }

    redis = RedisAdapter("sessions")
    redis.set(token, session)
    redis.expire(token, int(session["expireDate"]))
    return token

def destroy_session(session_id):
    """Destroys the given session"""
    redis = RedisAdapter("sessions")
    redis.unset(session_id)
    g.session = None

def authenticate(access_limit):
    """Authenticates an incoming requests and loads session information"""
    if request.endpoint in _public_paths:
        return
    elif request.method == "OPTIONS":
        return
    else:
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"].split(" ")
            if len(auth_header) == 2 and auth_header[0].upper() == "BEARER":
                token = auth_header[1]
                redis = RedisAdapter("sessions")
                session = redis.get(token)
                if session is not None:
                    if session["expireDate"] > time.time():
                        if session["clientIP"] == _get_request_ip():
                            if access_limit is not None:
                                if session["userRole"] not in access_limit:
                                    raise AccessDeniedError()
                            # Reset expiration date for session
                            session["expireDate"] = time.time() + (60 * 30)
                            g.session = session
                        else:
                            raise ClientOriginViolation()
                    else:
                        destroy_session(token)
                        raise SessionExpiredError()
                else:
                    raise InvalidSessionError()
            else:
                raise InvalidAuthorizationHeader()
        else:
            raise NoAuthorizationHeaderError()

def save_session():
    """Saves the current session state"""
    if "session" in g and g.session is not None and g.session["userRole"] != UserRole.APP:
        token = g.session["sessionToken"]
        redis = RedisAdapter("sessions")
        redis.set(token, g.session)

def noauth(fn):
    """Decorator to disable authentication for a single path."""
    fn.is_public = True
    return fn

def restrict_to(*roles):
    """Decorator to restrict access to certain user roles"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            f.access_limit = roles
            return f(*args, **kw)
        return wrapper
    return decorator

class NoAuthorizationHeaderError(APIException):
    def __init__(self):
        super(NoAuthorizationHeaderError, self).__init__(status_code=401, error_code=1101, message="No authorization header")

class SessionExpiredError(APIException):
    def __init__(self):
        super(SessionExpiredError, self).__init__(status_code=403, error_code=1102, message="Your session has expired")

class InvalidSessionError(APIException):
    def __init__(self):
        super(InvalidSessionError, self).__init__(status_code=403, error_code=1103, message="The session token provided is invalid")

class ClientOriginViolation(APIException):
    def __init__(self):
        super(ClientOriginViolation, self).__init__(status_code=403, error_code=1104, message="The request was sent from a new IP address, please login again")

class AccessDeniedError(APIException):
    def __init__(self):
        super(AccessDeniedError, self).__init__(status_code=403, error_code=1105, message="The access to this function is not allowed for the logged in user")

class InvalidAuthorizationHeader(APIException):
    def __init__(self):
        super(InvalidAuthorizationHeader, self).__init__(status_code=403, error_code=1106, message="The authorization header is invalid")