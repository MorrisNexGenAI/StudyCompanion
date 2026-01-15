
# ==================== urls.py (Main File) ====================
"""
Main urls.py file for the premium_users app.
All URL patterns are imported from the urls_patterns package.
"""
from django.urls import path
from .urls_patterns import admin_urlpatterns, api_urlpatterns

app_name = 'premium_users'

urlpatterns = [
    # ============= DJANGO TEMPLATE VIEWS (Admin UI) =============
    *admin_urlpatterns,
    
    # ============= API ENDPOINTS (React Frontend) =============
    *api_urlpatterns,
]

