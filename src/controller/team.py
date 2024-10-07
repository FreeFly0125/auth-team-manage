from model.Team import Team, TeamMember

def get_team_with_id(id):
    return Team.objects.get(id=id)
