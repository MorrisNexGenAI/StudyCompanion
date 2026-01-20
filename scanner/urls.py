# ==================== scanner/urls.py ====================
"""
Main project URLs
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('backend/', include('core.urls')),        # /backend/login/
    path('premium/', include('premium_users.urls')),
    path('', include('scan.urls')),                # All other scan URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)