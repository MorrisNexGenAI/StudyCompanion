# ==================== INIT: views_functions/__init__.py ====================
"""
Refactored views package for the premium_users app.
Each module handles a specific functionality area.
"""
from .user_management_views import (
    manage_premium_users,
    add_premium_user,
    edit_premium_user,
    toggle_user_status,
    delete_premium_user
)
from .topic_management_views import send_premium_topics, delete_premium_topic
from .api_views import (
    register_or_login,
    get_accessible_topics,
    get_departments_list,
    get_user_department,
    get_courses_by_department_and_year,
    get_topics_by_course,
    get_topic_full,
    get_available_years,
)
from .helper_views import (
    filter_topics_for_user,
    check_topic_access,
    get_active_premium_users_for_select
)

__all__ = [
    # User Management
    'manage_premium_users',
    'add_premium_user',
    'edit_premium_user',
    'toggle_user_status',
    'delete_premium_user',
    # Topic Management
    'send_premium_topics',
    'delete_premium_topic',
    # API
    'register_or_login',
    'get_accessible_topics',
    'get_departments_list',
    'get_user_department',
    'get_courses_by_department_and_year',
    'get_topics_by_course',
    'get_topic_full',
    'get_available_years',
    # Helpers
    'filter_topics_for_user',
    'check_topic_access',
    'get_active_premium_users_for_select',
]

