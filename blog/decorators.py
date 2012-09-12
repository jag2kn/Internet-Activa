from functools import wraps
from google.appengine.api import users
from flask import redirect, request

def isadmin():
    if not users.get_current_user():
        return False
    usuario = users.get_current_user()
    if usuario.email() == "jag2kn@gmail.com":
        return True
    if users.is_current_user_admin():
        return True
    return False

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view
    
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        if (isadmin()):
            return func(*args, **kwargs)
        if not users.is_current_user_admin():
            return redirect('/')
        return func(*args, **kwargs)
    return decorated_view
