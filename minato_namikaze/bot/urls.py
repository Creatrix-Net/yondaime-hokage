from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from botmain.views import *


urlpatterns = [ 
    path('keep_alive_bot', keep_alive, name="Keep Alive Bot"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
