from django.conf.urls import url
from . import views as signin

urlpatterns = [
    url("login/", signin,name='signin'),
    url("logout/", signin,name='log'),
]