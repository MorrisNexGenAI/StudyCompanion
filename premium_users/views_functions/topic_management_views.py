
# ==================== views_functions/topic_management_views.py ====================
"""
Topic management views - Send premium topics to users
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import PremiumUser
from scan.models import Topic


def send_premium_topics(request):
    """Main page to send premium topics to specific users."""
    premium_topics = Topic.objects.filter(
        is_premium=True,
        is_deleted=False  # Only show non-deleted topics
    ).select_related('course').order_by('-created_at')
    
    active_users = PremiumUser.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        selected_user_ids = request.POST.getlist('premium_users')
        
        if topic_id:
            topic = get_object_or_404(Topic, id=topic_id, is_premium=True, is_deleted=False)
            topic.premium_users.clear()
            if selected_user_ids:
                topic.premium_users.set(selected_user_ids)
            return redirect('premium_users:send_topics')
    
    topics_with_users = []
    for topic in premium_topics:
        assigned_users = topic.premium_users.filter(is_active=True)
        assigned_user_ids = list(assigned_users.values_list('id', flat=True))
        
        topics_with_users.append({
            'topic': topic,
            'assigned_users': assigned_users,
            'assigned_user_ids': assigned_user_ids,
            'assigned_count': assigned_users.count()
        })
    
    return render(request, 'premium_users/send_topics.html', {
        'topics_with_users': topics_with_users,
        'active_users': active_users,
        'total_topics': premium_topics.count(),
        'total_users': active_users.count()
    })


@login_required
def delete_premium_topic(request, topic_id):
    """Delete a premium topic"""
    topic = get_object_or_404(Topic, id=topic_id, is_premium=True)
    assigned_count = topic.premium_users.filter(is_active=True).count()
    
    if request.method == "POST":
        topic.delete()
        messages.success(request, f"✅ Premium topic '{topic.title}' deleted successfully.")
        return redirect("manage_premium_topics")
    
    # GET request — show confirmation
    return render(request, 'scan/partials/confirm_delete_topic.html', {
        'topic': topic,
        'assigned_count': assigned_count
    })

