from flask import Blueprint, g
from model.Team import Team, TeamMember
from util import response, validate
from controller import user as user_controller
from controller import team as team_controller
from error import APIException


team = Blueprint("team", __name__)


@team.route("/register", methods=["POST"])
@validate("team_registeration")
def register_team():
    if _check_team_available(g.payload["name"]):
        t = Team()
        t.name = g.payload["name"]
        t.admin = [str(g.session["userID"])]

        u = user_controller.get_user_by_id(id=g.session["userID"])
        u.role = "admin"
        u.save()

        m = TeamMember()
        m.user_id = str(g.session["userID"])
        m.first_name = u.first_name
        m.last_name = u.last_name
        m.mail = u.mail
        m.role = u.role

        t.members = [m]
        t.save()
        return response(success=True)
    else:
        raise TeamNameInvalidError()
    
@team.route("/rename", methods=["POST"])
@validate("team_rename")
def rename_team():
    if _check_team_available(g.payload["name"]):
        t = team_controller.get_team_with_id(g.payload["id"])
        t.name = g.payload["name"]
        t.save()
        return response(success=True)
    else:
        raise TeamNameInvalidError()


@team.route("/delete", methods=["DELETE"])
@validate("team_delete")
def delete_team():
    t = team_controller.get_team_with_id(g.payload["id"])
    t.delete()
    return response(success=True)


def _check_team_available(name):
    return (len(name) > 4) and (Team.objects(name=name).count() == 0)

class TeamNameInvalidError(APIException):
    def __init__(self):
        super(TeamNameInvalidError, self).__init__(status_code=409, error_code=1204, message="The team name is already registered in the system.")
