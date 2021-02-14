from django.urls import path
from botmain import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='Home'),
    path('keepalive/', views.home_view_alive,name='Keep Alive')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
