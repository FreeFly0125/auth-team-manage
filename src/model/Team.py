from database import db


class TeamMember(db.EmbeddedDocument):
    """Stores selected member information"""

    user_id = db.StringField(required=True)
    mail = db.StringField(required=True)
    first_name = db.StringField()
    last_name = db.StringField()
    role = db.StringField()


class Team(db.Document):
    """Stores team information"""

    name = db.StringField(required=True)
    admin = db.ListField(db.StringField(), default=list)
    members = db.ListField(db.EmbeddedDocumentField(TeamMember), default=list)
