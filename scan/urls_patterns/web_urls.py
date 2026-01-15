
# ==================== urls_patterns/web_urls.py ====================
"""
Web interface URLs - Main pages
"""
from django.urls import path
from .. import views

web_urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_new, name='scan_new'),
    path('upload/', views.upload_and_extract, name='upload_and_extract'),
    path('save/', views.save_topic, name='save_topic'),
    path('library/', views.library, name='library'),
    path('text-input/', views.text_input_page, name='text_input'),
    path('process-text/', views.process_text_input, name='process_text_input'),
]

