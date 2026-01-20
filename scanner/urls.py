# ==================== scanner/urls.py ====================
"""
Main project URLs
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('backend/', include('core.urls')),        # HTML admin login at /backend/login/
    path('api/', include('scan.urls_patterns.api_urls')),  # API endpoints at /api/auth/login/
    path('premium/', include('premium_users.urls')),
    path('', include('scan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)