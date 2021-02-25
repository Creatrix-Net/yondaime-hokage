from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from botmain.views import home, invite_bot, keep_alive, sendmessages
from account.views import *


urlpatterns = [ 
    path('admin/', admin.site.urls),

    path('keep_alive_bot', keep_alive, name="Keep Alive Bot"),
    
    path('', home, name="Home"),
    path('send/', sendmessages, name="Send"),
    path('invite/', invite_bot, name="Invite"),

    url(r'^accounts/', include('account.urls')),
    url(r'^discord/', include('discord_auth_data.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
