# ==================== views_functions/library_views.py ====================
"""
Library views - Browse courses and topics
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from ..models import Course, Topic


def library(request):
    """Display all courses with topic counts"""
    courses = Course.objects.filter(is_deleted=False).prefetch_related('departments')
    
    for course in courses:
        community_count = course.topics.filter(is_premium=False, is_deleted=False).count()
        unassigned_premium_count = course.topics.filter(
            is_premium=True,
            is_deleted=False,
            premium_users__isnull=True
        ).count()
        course.visible_topic_count = community_count + unassigned_premium_count
    
    return render(request, 'scan/partials/library.html', {'courses': courses})


def course_detail(request, course_id):
    """Display course with all accessible topics"""
    course = get_object_or_404(Course.objects.prefetch_related('departments'), id=course_id, is_deleted=False)
    topics = course.topics.filter(
        is_deleted=False
    ).filter(
        Q(is_premium=False) | Q(is_premium=True, premium_users__isnull=True)
    ).distinct()
    return render(request, 'scan/partials/course_detail.html', {
        'course': course,
        'topics': topics
    })


def course_full_summary(request, course_id):
    """Display full summary of all community topics in a course"""
    course = get_object_or_404(Course.objects.prefetch_related('departments'), id=course_id, is_deleted=False)
    full_text = ""
    community_topics = course.topics.filter(is_premium=False, is_deleted=False).order_by('order')
    for topic in community_topics:
        if topic.refined_summary:
            full_text += f"\n\n{'='*50}\nTOPIC: {topic.title}\n{'='*50}\n\n"
            full_text += topic.refined_summary
    return render(request, 'scan/partials/full_summary.html', {'course': course, 'full_text': full_text})


def topic_detail(request, topic_id):
    """
    View single topic.
    ADMIN (staff) has FULL ACCESS to all topics.
    Regular users are restricted based on premium assignment.
    """
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    
    # ADMIN ACCESS: If user is staff, allow full access
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'scan/partials/topic_detail.html', {'topic': topic})
    
    # NON-ADMIN: Block access to assigned premium topics
    if topic.is_premium and topic.premium_users.exists():
        return render(request, 'scan/partials/premium_access_denied.html', {
            'topic': topic,
            'assigned_count': topic.premium_users.count()
        })
    
    return render(request, 'scan/partials/topic_detail.html', {'topic': topic})

