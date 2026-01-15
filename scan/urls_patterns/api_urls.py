

# ==================== urls_patterns/topic_urls.py ====================
"""
Topic management URLs
"""
from django.urls import path
from .. import views

topic_urlpatterns = [
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.edit_refined_summary, name='edit_refined_summary'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('topic/<int:topic_id>/manage-assignments/', views.manage_topic_assignments, name='manage_topic_assignments'),
    path('manage-premium-topics/', views.manage_premium_topics, name='manage_premium_topics'),
]


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
