
# ==================== models.py (Main File) ====================
"""
Main models.py file for the scan app.
All models are imported from the models_functions package.
"""

from .models_functions import (
    Department,
    Course,
    Topic,
    AIRefine,
)

__all__ = [
    'Department',
    'Course',
    'Topic',
    'AIRefine',
]
