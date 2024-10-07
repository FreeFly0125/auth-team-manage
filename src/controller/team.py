from model.Team import Team

def get_teams_for_user(user_id):
    return Team.objects(members__user_id=user_id)


def get_team_with_id(id):
    return Team.objects.get(id=id)
