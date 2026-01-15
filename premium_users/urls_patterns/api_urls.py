# ==================== URLS: api_urls.py ====================
"""
API URLs - REST endpoints for React/mobile apps
Updated for Phase 5
"""
from django.urls import path
from .. import views

api_urlpatterns = [
    # Authentication
    path('api/register-or-login/', views.register_or_login, name='api_register'),
    
    # Departments
    path('api/departments/', views.get_departments_list, name='api_departments_list'),
    path('api/users/<int:user_id>/department/', views.get_user_department, name='api_user_department'),
    
    # Courses (with year filtering)
    path('api/departments/<int:department_id>/courses/', views.get_courses_by_department_and_year, name='api_courses_by_dept_year'),
    path('api/departments/<int:department_id>/years/', views.get_available_years, name='api_available_years'),
    
    # Topics
    path('api/courses/<int:course_id>/topics/', views.get_topics_by_course, name='api_topics_by_course'),
    path('api/topics/<int:topic_id>/', views.get_topic_full, name='api_topic_full'),
    
    # Legacy (backward compatibility)
    path('api/users/<int:user_id>/topics/', views.get_accessible_topics, name='api_user_topics'),
]

