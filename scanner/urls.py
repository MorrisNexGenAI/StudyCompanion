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
    path('auth/', include('core.urls')),           # ADD THIS - Authentication URLs
    path('premium/', include('premium_users.urls')),  # Premium users
    path('', include('scan.urls')),                # Main app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)