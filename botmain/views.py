from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse


from django.conf import settings

def keep_alive(request):
    src='<title>Minato Namikaze</title><script src="https://discordbotlist.com/widget/index.js" async></script></head>'
    htm1='<h1><dbl-stat bot-id="minato-namikaze" stat="guilds">Loading...</dbl-stat> guilds</h1>'
    html2='<br/><h1><dbl-stat bot-id="minato-namikaze" stat="users">Loading...</dbl-stat> users</h1>'
    return HttpResponse(src+htm1+html2)
