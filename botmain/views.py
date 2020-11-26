from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def home(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
