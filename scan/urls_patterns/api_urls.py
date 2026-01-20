# ==================== scan/api_urls.py ====================
"""
API URLs with proper structure
"""
from django.urls import path
from ..views_functions.api_views import (
    api_admin_bulk_download,
    api_admin_upload_users,
)
from ..views_functions.api_auth import (
    api_login,
    api_logout,
    api_me,
)
from .. import views

# These will be prefixed with /api/ in scanner/urls.py
urlpatterns = [
    # Authentication endpoints -> /api/auth/*
    path('auth/login/', api_login, name='api_login'),
    path('auth/logout/', api_logout, name='api_logout'),
    path('auth/me/', api_me, name='api_me'),
    
    # Data endpoints -> /api/departments/, etc.
    path('departments/', views.api_departments, name='api_departments'),
    path('departments/<int:dept_id>/courses/', views.api_department_courses, name='api_department_courses'),
    path('courses/<int:course_id>/topics/', views.api_course_topics, name='api_course_topics'),
    path('topics/<int:topic_id>/', views.api_topic_detail, name='api_topic_detail'),
    
    # Admin endpoints -> /api/admin/*
    path('admin/bulk-download/', api_admin_bulk_download, name='api_admin_bulk_download'),
    path('admin/upload-users/', api_admin_upload_users, name='api_admin_upload_users'),
]