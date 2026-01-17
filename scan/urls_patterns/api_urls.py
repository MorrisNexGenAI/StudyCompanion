


# ==================== urls_patterns/api_urls.py ====================
"""
Public API URLs - For mobile app
"""
from django.urls import path
from .. import views

api_urlpatterns = [
    path('api/departments/', views.api_departments, name='api_departments'),
    path('api/departments/<int:dept_id>/courses/', views.api_department_courses, name='api_department_courses'),
    path('api/courses/<int:course_id>/topics/', views.api_course_topics, name='api_course_topics'),
    path('api/topics/<int:topic_id>/', views.api_topic_detail, name='api_topic_detail'),
]
