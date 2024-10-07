"""Static routes

Blueprint defining static API routes.
"""

from flask import Blueprint
from util import response
from auth import noauth
import config
import time

static = Blueprint("static", __name__)

@static.route("/info", methods=["GET"])
def get_info():
    payload = {
        "apiVersion" : config.VERSION,
        "environment": config.ENVIRONMENT,
        "serverTime" : time.time()
    }
    return response(payload=payload)

@static.route("/ping", methods=["GET"])
@noauth
def ping_backend():
    return response(empty=True)