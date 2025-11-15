from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from photos.views import protected_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/photos/', include('photos.urls')),
    # protected media endpoint (replaces direct static serving for media files)
    path('api/media/<path:path>/', protected_media, name='protected-media'),
]

# Note: we do NOT add the default static() serving for MEDIA_URL here so that
# media files are served only through the protected_media endpoint which
# enforces authentication and ownership checks.