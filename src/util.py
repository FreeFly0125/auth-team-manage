""" Common utilities

This module defines helper functions and decorators that can be used accross
all submodules.
"""

from functools import wraps
from flask import request, g, jsonify, Response
import jsonschema
import error
import json


def get_request_ip():
    """Returns the requester's IP address regardless of proxying webservers and spoofed headers"""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        trusted_proxies = {"127.0.0.1", "172.31.14.107", "172.31.17.13"}
        route = request.access_route + [request.remote_addr]

        return next(
            (addr for addr in reversed(route) if addr not in trusted_proxies),
            request.remote_addr,
        )


def validate(schema):
    """Decorator to validate the JSON payload against a JSON schema"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            payload = request.get_json()
            if payload is None:
                raise error.NoJsonPayloadException()
            else:
                try:
                    jsonschema.validate(
                        payload,
                        json.load(open("schema/" + schema + ".json", "r")),
                        format_checker=jsonschema.FormatChecker(),
                    )
                    g.payload = payload
                except jsonschema.ValidationError as e:
                    raise error.MalformedPayloadException(e.message)
            return f(*args, **kw)

        return wrapper

    return decorator


def response(
    payload=None,
    status_code=200,
    error_code=None,
    error_message=None,
    success=None,
    empty=False,
):
    """Method to build the default API response"""
    if empty:
        response = ""
        status_code = 204
        r = Response()
    else:
        response = {}

        if error_code is not None:
            error = {"errorCode": error_code}
            if error_message is not None:
                error["errorMessage"] = error_message
            response["error"] = error

        if payload is not None:
            response["payload"] = payload
        elif success is not None:
            response["payload"] = {}
        if success is not None:
            response["payload"]["success"] = success

        r = jsonify(**response)

        if error_code is not None:
            r.headers.add("X-ErrorCode", error_code)

    r.status_code = status_code

    return r
