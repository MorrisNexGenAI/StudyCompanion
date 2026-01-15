
# ==================== urls_patterns/premium_urls.py ====================
"""
Premium user management URLs
"""
from django.urls import include, path

premium_urlpatterns = [
    path("premium/", include("premium_users.urls", namespace="premium_users")),
]