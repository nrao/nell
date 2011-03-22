from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import User as AuthUser
from nell.scheduler.models       import User

def associate(u, au):
    if u is not None and u.auth_user_id is None:
        print "Associcating", u.username, "with", au
        u.auth_user = au
        u.save()
        return au
    return None

users = [associate(User.objects.get(username = au.username), au) 
            for au in AuthUser.objects.all()]
print "Associated", len([u for u in users if u is not None]), "users."
