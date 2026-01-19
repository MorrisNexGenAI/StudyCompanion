# ==================== urls_patterns/__init__.py ====================
"""
Refactored URL patterns package for the scan app.
Each module handles a specific URL group.
"""

from .web_urls import web_urlpatterns
from .course_urls import course_urlpatterns
from .topic_urls import topic_urlpatterns
from .api_urls import api_urlpatterns
from .ai_urls import ai_urlpatterns
from .utility_urls import utility_urlpatterns


__all__ = [
    'web_urlpatterns',
    'course_urlpatterns',
    'topic_urlpatterns',
    'api_urlpatterns',
    'ai_urlpatterns',
    'utility_urlpatterns',
]

