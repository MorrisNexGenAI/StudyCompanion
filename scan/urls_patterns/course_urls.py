
# ==================== urls_patterns/course_urls.py ====================
"""
Course management URLs
"""
from django.urls import path
from .. import views

course_urlpatterns = [
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/full/', views.course_full_summary, name='course_full_summary'),
    path('create-course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
]