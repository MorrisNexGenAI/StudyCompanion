from django.urls import include, path
from . import views
from . import ai_views

urlpatterns = [
    # ============= WEB INTERFACE =============
    path('', views.home, name='home'),
    path('scan/', views.scan_new, name='scan_new'),
    path('upload/', views.upload_and_extract, name='upload_and_extract'),
    path('save/', views.save_topic, name='save_topic'),
    path('library/', views.library, name='library'),
    
    # Course URLs
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/full/', views.course_full_summary, name='course_full_summary'),
    path('create-course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Topic URLs
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.edit_refined_summary, name='edit_refined_summary'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('text-input/', views.text_input_page, name='text_input'),
    path('process-text/', views.process_text_input, name='process_text_input'),

    # Utilities
    path('ocr-status/', views.ocr_status, name='ocr_status'),
    
    # ============= PUBLIC API (Mobile App) =============
    path('api/departments/', views.api_departments, name='api_departments'),
    path('api/departments/<int:dept_id>/courses/', views.api_department_courses, name='api_department_courses'),
    path('api/courses/<int:course_id>/topics/', views.api_course_topics, name='api_course_topics'),
    path('api/topics/<int:topic_id>/', views.api_topic_detail, name='api_topic_detail'),
    path('topic/<int:topic_id>/manage-assignments/', views.manage_topic_assignments, name='manage_topic_assignments'),
    path('manage-premium-topics/', views.manage_premium_topics, name='manage_premium_topics'),
      # AI Refine Routes
    path('topics/<int:topic_id>/ai-refine/', ai_views.ai_refine_page, name='ai_refine_page'),
    path('topics/<int:topic_id>/generate-ai/', ai_views.generate_ai_refine, name='generate_ai_refine'),
    path('topics/<int:topic_id>/select-ai/', ai_views.select_ai_refine, name='select_ai_refine'),
    path('ai-status/', ai_views.ai_status, name='ai_status'),


    # Premium User Management Setting
    path("premium/", include("premium_users.urls", namespace="premium_users"))
]

