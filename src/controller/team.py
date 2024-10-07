from model.Team import Team

def get_teams_for_user(user_id):
    return Team.objects(members__user_id=user_id)


def get_team_with_id(id):
    return Team.objects.get(id=id)


def remove_user_from_team(user_id):
    Team.objects(members__user_id=user_id).update(pull__members__user_id=user_id)


def is_user_team_member(team_id, user_id):
    member = Team.objects(id=team_id, members__user_id=user_id).first()
    return member is not None
