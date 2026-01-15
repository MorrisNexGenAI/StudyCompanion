# ==================== views_functions/topic_management_views.py ====================
"""
Topic management views - Edit, delete, and manage topic assignments
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from ..models import Topic
from premium_users.models import PremiumUser


@csrf_exempt
def edit_refined_summary(request, topic_id):
    """
    Edit refined summary.
    ADMIN (staff) can edit ANY topic, even assigned premium ones.
    """
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    
    # NON-ADMIN users are restricted
    if not (request.user.is_authenticated and request.user.is_staff):
        if topic.is_premium and topic.premium_users.exists():
            messages.error(request, "You cannot edit assigned premium topics.")
            return redirect('topic_detail', topic_id=topic.id)
    
    if request.method == 'POST':
        refined_text = request.POST.get('refined_summary', '').strip()
        topic.refined_summary = refined_text
        topic.save()
        messages.success(request, "Refined summary updated successfully.")
        return redirect('topic_detail', topic_id=topic.id)
    
    return render(request, 'scan/partials/edit_refined.html', {'topic': topic})


def delete_topic(request, topic_id):
    """Soft delete a topic"""
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id=topic_id)
        course_id = topic.course.id
        topic.soft_delete()
        messages.success(request, f"Topic '{topic.title}' deleted successfully.")
        return redirect('course_detail', course_id=course_id)
    return redirect('library')


def manage_topic_assignments(request, topic_id):
    """Manage which premium users can access a specific premium topic"""
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    if not topic.is_premium:
        messages.error(request, "This is a community topic - no user assignments needed.")
        return redirect('topic_detail', topic_id=topic.id)

    active_users = PremiumUser.objects.filter(is_active=True).order_by('name')
    current_user_ids = list(topic.premium_users.values_list('id', flat=True))

    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('premium_users')
        topic.premium_users.clear()
        if selected_user_ids:
            topic.premium_users.set(selected_user_ids)
            count = len(selected_user_ids)
            messages.success(request, f"Topic assigned to {count} user{'s' if count != 1 else ''}!")
        else:
            messages.warning(request, "No users selected. Topic is not visible to anyone.")
        return redirect('topic_detail', topic_id=topic.id)

    return render(request, 'scan/partials/manage_topic_assignments.html', {
        'topic': topic,
        'course': topic.course,
        'active_users': active_users,
        'current_user_ids': current_user_ids
    })


def manage_premium_topics(request):
    """Admin page to manage all premium topics."""
    premium_topics = Topic.objects.filter(
        is_premium=True,
        is_deleted=False
    ).prefetch_related('course', 'premium_users').order_by('-updated_at')

    active_users = PremiumUser.objects.filter(is_active=True).order_by('name')

    topics_with_users = []
    for topic in premium_topics:
        assigned_users = topic.premium_users.all()
        topics_with_users.append({
            'topic': topic,
            'assigned_users': assigned_users,
            'assigned_user_ids': list(assigned_users.values_list('id', flat=True)),
            'assigned_count': assigned_users.count()
        })

    return render(request, 'scan/partials/manage_premium_topics.html', {
        'topics_with_users': topics_with_users,
        'active_users': active_users,
        'total_topics': premium_topics.count(),
        'total_users': active_users.count()
    })
