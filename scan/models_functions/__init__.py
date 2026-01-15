# ==================== models_functions/__init__.py ====================
"""
Refactored models package for the scan app.
Each module handles a specific model.
"""

from .department_model import Department
from .course_model import Course
from .topic_model import Topic
from .ai_refine_model import AIRefine

__all__ = [
    'Department',
    'Course',
    'Topic',
    'AIRefine',
]
