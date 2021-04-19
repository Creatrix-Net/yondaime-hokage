from functools import wraps
from django.urls import reverse
from django.http import HttpResponseRedirect


#the decorator
def myuser_login_required(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if str(request.session.session_key) not in request.session.keys():
            return HttpResponseRedirect(reverse("discord_bind_index"))
        return view_func(request, *args, **kwargs)
    return wrap