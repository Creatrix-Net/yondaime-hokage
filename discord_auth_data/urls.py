from __future__ import unicode_literals

from django.conf.urls import url
from django.urls import path


from . import views

urlpatterns = [
    url(r'^$', views.index, name='Signin'), #Signin
    path('logout/', views.logout, name="Logout"),
    
    url(r'^cb$', views.callback, name='discord_bind_callback'),
    
]
