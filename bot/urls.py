from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from botmain.views import home
from account.views import *


urlpatterns = [ 
    path('admin/', admin.site.urls),
    
    path('', home, name="Home"),
    url(r'^accounts/', include('account.urls')),
    url(r'^discord/', include('discord_auth_data.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
