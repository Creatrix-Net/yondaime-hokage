from django.conf.urls import url
from .views import signin,signout,view_profile,change_password

urlpatterns = [
    url(r"^login/$", signin,name='signin'),
    url(r"^logout/$", signout,name='signout'),
    url(r"^profile/$",view_profile,name="Profile"),
    url(r"^changepassword/$",change_password,name="Change Password")
]