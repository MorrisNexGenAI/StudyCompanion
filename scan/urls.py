from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_new, name='scan_new'),
    path('upload/', views.upload_and_extract, name='upload_and_extract'),
    path('save/', views.save_topic, name='save_topic'),
    path('library/', views.library, name='library'),
    
    # Course URLs
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/full/', views.course_full_summary, name='course_full_summary'),
    path('create-course/', views.create_course, name='create_course'),  # ← THIS WAS MISSING!
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),  # optional but good to have

    # Topic URLs
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.edit_refined_summary, name='edit_refined_summary'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),  # optional

    # API
    path('ocr-status/', views.ocr_status, name='ocr_status'),
]