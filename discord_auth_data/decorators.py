from functools import wraps
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied


#the login decorator
def myuser_login_required(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if str(request.session.session_key) not in request.session.keys():
            return HttpResponseRedirect(reverse("discord_bind_index"))
        else:
            userid = request.session[str(request.session.session_key)]['data']['uid']
            if str(userid) not in str(userid):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrap

#check manage server perms
def myuser_manage_server_perms(view_func):
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        if str(request.session.session_key) not in request.session.keys():
            return HttpResponseRedirect(reverse("discord_bind_index"))
        else:
            guilds = request.session[str(request.session.session_key)]['data']['guilds']
            path = str(request.get_full_path).split('/')[-1] #dashboard/userid/guildid
            for i in guilds:
                if int(path) != int(i.id):
                    raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrap