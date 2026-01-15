
# ==================== views.py (Main File) ====================
"""
Main views.py file for the scan app.
All view functions are imported from the views_functions package.
"""

from .views_functions import (
    # Home
    home,
    
    # Scanning
    scan_new,
    upload_and_extract,
    save_topic,
    
    # Library
    library,
    course_detail,
    course_full_summary,
    topic_detail,
    
    # Topic Management
    edit_refined_summary,
    delete_topic,
    manage_topic_assignments,
    manage_premium_topics,
    
    # Course Management
    create_course,
    delete_course,
    
    # Text Input
    text_input_page,
    process_text_input,
    
    # API
    api_departments,
    api_course_topics,
    api_topic_detail,
    api_department_courses,
    ocr_status,
)