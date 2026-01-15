
# ==================== urls_patterns/utility_urls.py ====================
"""
Utility URLs - Status checks and utilities
"""
from django.urls import path
from .. import views

utility_urlpatterns = [
    path('ocr-status/', views.ocr_status, name='ocr_status'),
]

