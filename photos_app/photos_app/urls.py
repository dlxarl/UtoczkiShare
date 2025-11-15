from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from photos.views import protected_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/photos/', include('photos.urls')),
 
    path('api/media/<path:path>/', protected_media, name='protected-media'),
]