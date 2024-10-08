"""User routes

Blueprint defining routes for user and session management.
"""

import hashlib
import time
import random

from flask import Blueprint, g

import auth
from auth import noauth
from controller import user as user_controller
from error import APIException
from util import response, validate
from model.User import User

user = Blueprint("user", __name__)


@user.route("/info", methods=["GET"])
def get_user_data():
    u = user_controller.get_user_by_id(id=g.session["userID"])

    payload = {"mail": u.mail}

    if u.first_name is not None:
        payload["first_name"] = u.first_name
    if u.last_name is not None:
        payload["last_name"] = u.last_name

    return response(payload=payload)


@user.route("/register", methods=["POST"])
@noauth
@validate("user_registration")
def register_user():
    if _check_password(g.payload["password"]):
        if _mail_available(g.payload["mail"]):
            u = User()
            u.mail = g.payload["mail"]
            if "firstName" in g.payload:
                u.first_name = g.payload["firstName"]
            if "lastName" in g.payload:
                u.last_name = g.payload["lastName"]
            if "role" in g.payload and g.payload["role"] != "user":
                raise APIException(
                    message="Only normal users can be registered using this path at the moment",
                    status_code=403,
                )
            else:
                u.role = "user"

            password_salt = _hash(str(time.time()) + str(random.random()))
            password_hash = _hash(g.payload["password"] + password_salt)

            u.password_hash = password_hash
            u.password_salt = password_salt

            u.save()
            return response(success=True)
        else:
            raise UsernameTakenError()
    else:
        raise InvalidPasswordFormatError()


@user.route("/update", methods=["POST"])
@validate("user_update")
def update_user_details():
    u = user_controller.get_user_by_id(id=g.session["userID"])

    if "firstName" in g.payload:
        u.first_name = g.payload["firstName"]
    if "lastName" in g.payload:
        u.last_name = g.payload["lastName"]
    if "role" in g.payload and g.payload["role"] != "user":
        raise APIException(
            message="Only normal users can be registered using this path at the moment",
            status_code=403,
        )

    if "password" in g.payload:
        if _check_password(g.payload["password"]):
            password_salt = _hash(str(time.time()) + str(random.random()))
            password_hash = _hash(g.payload["password"] + password_salt)

            u.password_hash = password_hash
            u.password_salt = password_salt
        else:
            raise InvalidPasswordFormatError()

    u.save()
    return response(success=True)


@user.route("/login", methods=["POST"])
@noauth
@validate("user_login")
def user_login():
    try:
        u = user_controller.get_user_by_mail(mail=g.payload["mail"])

        password_hash = _hash(g.payload["password"] + u.password_salt)
        if password_hash == u.password_hash:
            token = auth.start_session(u.id, u.role)
            return response(payload={"token": token})
        else:
            raise InvalidCredentialsError()
    except User.DoesNotExist:
        raise InvalidCredentialsError()


@user.route("/logout", methods=["POST"])
def user_logout():
    auth.destroy_session(g.session["sessionToken"])
    return response(success=True)


def _check_password(password):
    return len(password) > 4


def _mail_available(mail):
    return User.objects(mail=mail).count() == 0


def _hash(string):
    return str(hashlib.sha1(string.encode("utf-8")).hexdigest())


class InvalidPasswordFormatError(APIException):
    def __init__(self):
        super(InvalidPasswordFormatError, self).__init__(
            status_code=400,
            error_code=1201,
            message="Password must be at least 5 characters in length",
        )


class UsernameTakenError(APIException):
    def __init__(self):
        super(UsernameTakenError, self).__init__(
            status_code=409,
            error_code=1202,
            message="The e-mail is already registered in the system",
        )


class InvalidCredentialsError(APIException):
    def __init__(self):
        super(InvalidCredentialsError, self).__init__(
            status_code=403,
            error_code=1203,
            message="Userame and password do not match any account",
        )
