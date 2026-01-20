
from django.urls import path
from .urls_patterns import (
    web_urlpatterns,
    course_urlpatterns,
    topic_urlpatterns,
    urlpatterns,
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
    
    # ============= AI REFINE =============
    *ai_urlpatterns,
    *urlpatterns,


    
    # ============= UTILITIES =============
    *utility_urlpatterns,
    
]