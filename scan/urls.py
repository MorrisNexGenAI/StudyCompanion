# ==================== urls.py (Main File) ====================
"""
Main urls.py file for the scan app.
All URL patterns are imported from the urls_patterns package.
"""
from django.urls import path
from .urls_patterns import (
    web_urlpatterns,
    course_urlpatterns,
    topic_urlpatterns,
    api_urlpatterns,
    ai_urlpatterns,
    utility_urlpatterns,
    
)

urlpatterns = [
    # ============= WEB INTERFACE =============
    *web_urlpatterns,
    
    # ============= COURSE MANAGEMENT =============
    *course_urlpatterns,
    
    # ============= TOPIC MANAGEMENT =============
    *topic_urlpatterns,
    
    # ============= PUBLIC API (Mobile App) =============
    *api_urlpatterns,
    
    # ============= AI REFINE =============
    *ai_urlpatterns,
    
    # ============= UTILITIES =============
    *utility_urlpatterns,
    
   
]
