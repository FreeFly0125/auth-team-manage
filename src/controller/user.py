from model.User import User, UserRole

def get_user_by_id(id):
    return User.objects.get(id=id)

def get_user_by_mail(mail):
    return User.objects.get(mail=mail)
