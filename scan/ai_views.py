
# ==================== ai_views.py (Main File) ====================
"""
Main AI views.py file for the scan app.
All AI view functions are imported from the ai_views_functions package.
"""

from .ai_views_functions import (
    ai_refine_page,
    generate_ai_refine,
    select_ai_refine,
    ai_status,
)

__all__ = [
    'ai_refine_page',
    'generate_ai_refine',
    'select_ai_refine',
    'ai_status',
]