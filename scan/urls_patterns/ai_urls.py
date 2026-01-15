
# ==================== urls_patterns/ai_urls.py ====================
"""
AI Refine URLs - AI-powered text refinement
"""
from django.urls import path
from .. import ai_views

ai_urlpatterns = [
    path('topics/<int:topic_id>/ai-refine/', ai_views.ai_refine_page, name='ai_refine_page'),
    path('topics/<int:topic_id>/generate-ai/', ai_views.generate_ai_refine, name='generate_ai_refine'),
    path('topics/<int:topic_id>/select-ai/', ai_views.select_ai_refine, name='select_ai_refine'),
    path('ai-status/', ai_views.ai_status, name='ai_status'),
]

