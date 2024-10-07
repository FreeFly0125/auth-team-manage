"""User information

Class to easily access and modify user information
"""

from database import db

class UserRole:
    USER = "user"
    ADMIN = "admin"


class User(db.Document):
    """Stores user information"""
    mail = db.StringField(required=True)
    first_name = db.StringField()
    last_name = db.StringField()

    role = db.StringField(required=True, default="user", choices=(UserRole.USER, UserRole.ADMIN))

    password_hash = db.StringField(required=True)
    password_salt = db.StringField(required=True)