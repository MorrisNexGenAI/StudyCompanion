# ==================== core/urls.py ====================
"""
URL patterns for core authentication
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('account/', views.account_settings, name='account_settings'),
    path('admin-reset-password/', views.admin_password_reset, name='admin_password_reset'),
]

