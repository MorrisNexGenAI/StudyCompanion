# ==================== views_functions/__init__.py ====================
"""
Refactored views package for the scan app.
Each module handles a specific functionality area.
"""

from .home_views import home
from .scan_views import scan_new, upload_and_extract, save_topic
from .library_views import library, course_detail, course_full_summary, topic_detail
from .topic_management_views import edit_refined_summary, delete_topic, manage_topic_assignments, manage_premium_topics
from .course_management_views import create_course, delete_course
from .text_input_views import text_input_page, process_text_input
from .api_views import (
    api_departments,
    api_course_topics,
    api_topic_detail,
    api_department_courses,
    ocr_status
)

__all__ = [
    # Home
    'home',
    
    # Scanning
    'scan_new',
    'upload_and_extract',
    'save_topic',
    
    # Library
    'library',
    'course_detail',
    'course_full_summary',
    'topic_detail',
    
    # Topic Management
    'edit_refined_summary',
    'delete_topic',
    'manage_topic_assignments',
    'manage_premium_topics',
    
    # Course Management
    'create_course',
    'delete_course',
    
    # Text Input
    'text_input_page',
    'process_text_input',
    
    # API
    'api_departments',
    'api_course_topics',
    'api_topic_detail',
    'api_department_courses',
    'ocr_status',
]

