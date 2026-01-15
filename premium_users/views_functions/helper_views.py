# ==================== views_functions/helper_views.py ====================
"""
Helper views - Utility functions used by other apps
"""
from django.db.models import Q

from ..models import PremiumUser


def filter_topics_for_user(topics_queryset, user_id=None):
    """Filter topics based on user access + exclude soft-deleted."""
    # Always exclude soft-deleted topics
    topics_queryset = topics_queryset.filter(is_deleted=False)
    
    if not user_id:
        return topics_queryset.filter(is_premium=False)

    try:
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        return topics_queryset.filter(
            Q(is_premium=False) | Q(is_premium=True, premium_users=user)
        ).distinct()
    except PremiumUser.DoesNotExist:
        return topics_queryset.filter(is_premium=False)


def check_topic_access(topic, user_id=None):
    """
    Check if a specific user can access a specific topic.
    
    RULES:
    - Community topic → Always True
    - Premium topic + no user_id → False
    - Premium topic + user_id → True ONLY if user is explicitly assigned
    """
    # Community topics are accessible to everyone
    if not topic.is_premium:
        return True

    # Premium topic with no user_id = no access
    if not user_id:
        return False

    try:
        # Check if user exists and is active
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        
        # Check if this user is explicitly assigned to this topic
        return topic.is_accessible_by(user)
    
    except PremiumUser.DoesNotExist:
        return False


def get_active_premium_users_for_select():
    """Get all active premium users (for assignment dropdowns)"""
    return PremiumUser.objects.filter(is_active=True).order_by('name')
