# ==================== views_functions/api_views.py ====================
"""
API views - Public API endpoints for mobile app
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from ..models import Course, Topic, Department
from ..utils.ocr import test_ocr_connection
from premium_users.views import filter_topics_for_user, check_topic_access


def api_departments(request):
    """Get all departments"""
    departments = Department.objects.all()
    return JsonResponse([{'id': d.id, 'name': d.name} for d in departments], safe=False)


def api_course_topics(request, course_id):
    """Get all topics for a course (filtered by user access)"""
    course = get_object_or_404(Course, id=course_id, is_deleted=False)
    user_id = request.GET.get('user_id') or request.headers.get('X-User-ID')
    topics = filter_topics_for_user(course.topics.filter(is_deleted=False), user_id)
    data = [{
        'id': t.id,
        'title': t.title,
        'page_range': t.page_range,
        'updated_at': int(t.updated_at.timestamp()),
        'is_refined': t.is_refined(),
        'is_premium': t.is_premium,
    } for t in topics]
    return JsonResponse(data, safe=False)


def api_topic_detail(request, topic_id):
    """Get detailed information about a specific topic"""
    topic = get_object_or_404(
        Topic.objects.select_related('course').prefetch_related('course__departments'), 
        id=topic_id,
        is_deleted=False
    )
    user_id = request.GET.get('user_id') or request.headers.get('X-User-ID')
    if not check_topic_access(topic, user_id):
        return JsonResponse({
            'error': 'Access denied. This is a premium topic.',
            'is_premium': True,
            'requires_login': True
        }, status=403)

    data = {
        'id': topic.id,
        'title': topic.title,
        'page_range': topic.page_range,
        'refined_summary': topic.refined_summary,
        'raw_text': topic.raw_text,
        'course_name': topic.course.name,
        'course_year': topic.course.year,
        'departments': [d.name for d in topic.course.departments.all()],
        'updated_at': int(topic.updated_at.timestamp()),
        'created_at': int(topic.created_at.timestamp()),
        'is_premium': topic.is_premium,
    }
    return JsonResponse(data)


def api_department_courses(request, dept_id):
    """Get all courses in a department (with topic counts filtered by user access)"""
    department = get_object_or_404(Department, id=dept_id)
    courses = department.courses.filter(is_deleted=False).prefetch_related('departments')
    user_id = request.GET.get('user_id') or request.headers.get('X-User-ID')
    data = []
    for course in courses:
        accessible_topics = filter_topics_for_user(course.topics.filter(is_deleted=False), user_id)
        data.append({
            'id': course.id,
            'name': course.name,
            'year': course.year,
            'departments': [{'id': d.id, 'name': d.name} for d in course.departments.all()],
            'topic_count': accessible_topics.count(),
            'refined_count': accessible_topics.filter(refined_summary__isnull=False).exclude(refined_summary='').count(),
        })
    return JsonResponse(data, safe=False)


def ocr_status(request):
    """Check OCR service health status"""
    is_healthy, message = test_ocr_connection()
    return JsonResponse({'healthy': is_healthy, 'message': message})

