from django.conf.urls import url
from .views import signin,signout

urlpatterns = [
    url(r"^login/$", signin,name='signin'),
    url(r"^logout/$", signout,name='signout'),
]