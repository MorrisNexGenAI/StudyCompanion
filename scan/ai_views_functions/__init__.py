# ==================== ai_views_functions/__init__.py ====================
"""
Refactored AI views package for the scan app.
Each module handles a specific AI functionality.
"""

from .ai_refine_views import ai_refine_page, generate_ai_refine, select_ai_refine
from .ai_status_views import ai_status

__all__ = [
    'ai_refine_page',
    'generate_ai_refine',
    'select_ai_refine',
    'ai_status',
]
