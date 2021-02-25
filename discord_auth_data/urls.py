from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='discord_bind_index'),
    url(r'^cb$', views.callback, name='discord_bind_callback'),
]
