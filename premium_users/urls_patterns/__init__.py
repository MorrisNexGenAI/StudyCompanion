
# ==================== urls_patterns/__init__.py ====================
"""
Refactored URL patterns package for the premium_users app.
Each module handles a specific URL group.
"""

from .admin_urls import admin_urlpatterns
from .api_urls import api_urlpatterns

__all__ = [
    'admin_urlpatterns',
    'api_urlpatterns',
]

