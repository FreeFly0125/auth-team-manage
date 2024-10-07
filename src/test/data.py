""" Test data module

Running this module will create some database entries for testing purposes.
"""

import sys
import os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import time
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from flask import Flask
import requests

import config
import database
from model.User import User, UserRole
from routes.user.route import _hash


if __name__ == '__main__':
    app = Flask(__name__)
    app.config["MONGODB_SETTINGS"] = {
        "db" : "bluquist_" + config.ENVIRONMENT,
        "host" : config.MONGO
    }
    database.db.init_app(app)

    print("Wipe the database")
    db = MongoClient(config.MONGO)
    db.drop_database("bluquist_" + config.ENVIRONMENT)

    print("Register test users.", end="")

    u = User()
    u.mail = "test@user.com"
    u.role = UserRole.USER
    password_salt = _hash(str(time.time()) + str(random.random()))
    password_hash = _hash("test123" + password_salt)
    u.password_hash = password_hash
    u.password_salt = password_salt