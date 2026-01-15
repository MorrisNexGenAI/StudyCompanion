
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