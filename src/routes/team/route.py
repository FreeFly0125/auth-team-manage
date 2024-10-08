from flask import Blueprint, g, request
from model.Team import Team, TeamMember
from util import response, validate
from controller import user as user_controller
from controller import team as team_controller
from error import APIException
from functools import wraps


team = Blueprint("team", __name__)


def verify_team_access(f):
    # Verify the access to team data
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            t = team_controller.get_team_with_id(g.payload["teamID"])
        except Team.DoesNotExist:
            raise TeamNotExistError()
        # if the logged in user is super user with UserRole.Admin, it would be able to access all teams
        # to avoid confussion, used UserRole.APP as super user role
        if (
            g.session["userRole"] != "appadmin"
            and str(g.session["userID"]) not in t.admin
        ):
            raise AccessDeniedError()
        return f(*args, **kw)

    return wrapper


@team.route("/info", methods=["Get"])
def get_team_info():
    team_id = request.args.get("team_id")

    if team_id:
        # if there's particular team id, returns the corresponding team data
        try:
            t = team_controller.get_team_with_id(team_id)
        except Team.DoesNotExist:
            raise TeamNotExistError()
        print(t.members[0]["user_id"])
        print(str(g.session["userID"]))
        if g.session["userRole"] != "appadmin" and not any(
            member["user_id"] == str(g.session["userID"]) for member in t.members
        ):
            raise AccessDeniedError()

        t = team_controller.get_team_with_id(team_id)
        return response(payload=t)
    else:
        # if there's no particular team id, returns the whole team data that the logged user is in
        teams = team_controller.get_teams_for_user(str(g.session["userID"]))
        return response(payload=teams)


@team.route("/register", methods=["POST"])
@validate("team_registeration")
def register_team():
    if _check_team_available(g.payload["name"]):
        # check if the team name is creatable
        t = Team()
        t.name = g.payload["name"]
        t.admin = [str(g.session["userID"])]

        u = user_controller.get_user_by_id(id=g.session["userID"])
        m = TeamMember()
        m.user_id = str(g.session["userID"])
        m.first_name = u.first_name
        m.last_name = u.last_name
        m.mail = u.mail
        m.role = "admin"

        t.members = [m]
        t.save()
        return response(success=True)
    else:
        raise TeamNameInvalidError()


@team.route("/rename", methods=["POST"])
@validate("team_rename")
@verify_team_access
def rename_team():
    if _check_team_available(g.payload["name"]):
        # check if the team name is creatable
        t = team_controller.get_team_with_id(g.payload["teamID"])
        t.name = g.payload["name"]
        t.save()
        return response(success=True)
    else:
        raise TeamNameInvalidError()


@team.route("/delete", methods=["DELETE"])
@validate("team_delete")
@verify_team_access
def delete_team():
    t = team_controller.get_team_with_id(g.payload["teamID"])
    t.delete()
    return response(success=True)


@team.route("/members", methods=["POST"])
@validate("modify_members")
@verify_team_access
def add_team_member():
    if team_controller.is_user_team_member(g.payload["teamID"], g.payload["userID"]):
        raise UserExistInTeamError()

    u = user_controller.get_user_by_id(id=g.payload["userID"])
    m = TeamMember()
    m.user_id = g.payload["userID"]
    m.first_name = u.first_name
    m.last_name = u.last_name
    m.mail = u.mail
    m.role = u.role

    t = team_controller.get_team_with_id(g.payload["teamID"])
    t.members.append(m)
    t.save()
    return response(success=True)


@team.route("/members", methods=["DELETE"])
@validate("modify_members")
@verify_team_access
def delete_team_member():
    if not team_controller.is_user_team_member(
        g.payload["teamID"], g.payload["userID"]
    ):
        raise UserNotExistError()

    team_controller.remove_user_from_team(g.payload["teamID"], g.payload["userID"])
    return response(success=True)


@team.route("/change_role", methods=["PATCH"])
@validate("change_user_role")
@verify_team_access
def change_user_role():
    if not team_controller.is_user_team_member(
        g.payload["teamID"], g.payload["userID"]
    ):
        raise UserNotExistError()

    t = team_controller.get_team_with_id(g.payload["teamID"])
    if g.payload["role"] == "user":
        if g.payload["userID"] not in t.admin:
            raise UserAlreadySameRoleError()

        team_controller.update_user_role(
            g.payload["teamID"], g.payload["userID"], "user"
        )
        t.admin.remove(g.payload["userID"])
    elif g.payload["role"] == "admin":
        if g.payload["userID"] in t.admin:
            raise UserAlreadySameRoleError()

        team_controller.update_user_role(
            g.payload["teamID"], g.payload["userID"], "admin"
        )
        t.admin.append(g.payload["userID"])
    t.save()
    return response(success=True)


def _check_team_available(name):
    return (len(name) > 4) and (Team.objects(name=name).count() == 0)


class TeamNameInvalidError(APIException):
    def __init__(self):
        super(TeamNameInvalidError, self).__init__(
            status_code=409,
            error_code=1204,
            message="The team name is already registered in the system.",
        )


class TeamNotExistError(APIException):
    def __init__(self):
        super(TeamNotExistError, self).__init__(
            status_code=400, error_code=1205, message="The team is not found."
        )


class AccessDeniedError(APIException):
    def __init__(self):
        super(AccessDeniedError, self).__init__(
            status_code=403,
            error_code=1105,
            message="The access to this function is not allowed for the logged in user",
        )


class UserExistInTeamError(APIException):
    def __init__(self):
        super(UserExistInTeamError, self).__init__(
            status_code=409,
            error_code=1206,
            message="The user is already existing within the team.",
        )


class UserNotExistError(APIException):
    def __init__(self):
        super(UserNotExistError, self).__init__(
            status_code=404,
            error_code=1207,
            message="The user is not found within the team.",
        )


class UserAlreadySameRoleError(APIException):
    def __init__(self):
        super(UserAlreadySameRoleError, self).__init__(
            status_code=409,
            error_code=1208,
            message="The user is already set as the role.",
        )
