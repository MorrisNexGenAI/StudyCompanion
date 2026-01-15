# ==================== MAIN: views.py ====================
"""
Main views.py file for the premium_users app.
All view functions are imported from the views_functions package.
"""
from .views_functions import (
    # User Management
    manage_premium_users,
    add_premium_user,
    edit_premium_user,
    toggle_user_status,
    delete_premium_user,
    # Topic Management
    send_premium_topics,
    delete_premium_topic,
    # API
    register_or_login,
    get_accessible_topics,
    get_departments_list,
    get_user_department,
    get_courses_by_department_and_year,
    get_topics_by_course,
    get_topic_full,
    get_available_years,
    # Helpers
    filter_topics_for_user,
    check_topic_access,
    get_active_premium_users_for_select,
)
