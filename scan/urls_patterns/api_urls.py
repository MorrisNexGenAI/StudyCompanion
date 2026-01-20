


# ==================== urls_patterns/api_urls.py ====================
"""
Public API URLs - For mobile app
"""
from django.urls import path
from .. import views
from django.utils import timezone
from ..views_functions.api_views import (
    # ... existing imports ...
    api_admin_bulk_download,
    api_admin_upload_users,
)
from ..views_functions.api_auth import (
    api_login,
    api_logout,
    api_me,
)
    


api_urlpatterns = [
    path('api/departments/', views.api_departments, name='api_departments'),
    path('api/departments/<int:dept_id>/courses/', views.api_department_courses, name='api_department_courses'),
    path('api/courses/<int:course_id>/topics/', views.api_course_topics, name='api_course_topics'),
    path('api/topics/<int:topic_id>/', views.api_topic_detail, name='api_topic_detail'),
    path('api/admin/bulk-download/', api_admin_bulk_download, name='api_admin_bulk_download'),
    path('api/admin/upload-users/', api_admin_upload_users, name='api_admin_upload_users'),
    path("auth/login/", api_login),
    path("auth/logout/", api_logout),
    path("auth/me/", api_me),
]