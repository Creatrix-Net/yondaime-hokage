from __future__ import unicode_literals

from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^$', views.index, name='Select Server'),
    path('announcement/<int:userid>/<int:serverid>/', views.announcements, name='Announcement'),
]
