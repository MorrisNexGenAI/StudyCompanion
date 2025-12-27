from django.urls import path
from . import views

app_name = 'premium_users'

urlpatterns = [
    # ============= DJANGO TEMPLATE VIEWS (Admin UI) =============
    path('manage/', views.manage_premium_users, name='manage_users'),
    path("add/", views.add_premium_user, name="add_user"),
    path('send-topics/', views.send_premium_topics, name='send_topics'),
   path("delete-topic/<int:topic_id>/",views.delete_premium_topic,name="delete_premium_topic"),



    path('edit/<int:user_id>/', views.edit_premium_user, name='edit_user'),
    path('toggle/<int:user_id>/', views.toggle_user_status, name='toggle_status'),
    path('delete/<int:user_id>/', views.delete_premium_user, name='delete_user'),
    
    # ============= API ENDPOINTS (React Frontend) =============
    path('api/register-or-login/', views.register_or_login, name='api_register'),
    path('api/users/<int:user_id>/topics/', views.get_accessible_topics, name='api_user_topics'),
]




