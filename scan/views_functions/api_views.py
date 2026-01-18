# ==================== views_functions/api_views.py ====================
"""
API views - Public API endpoints for mobile app
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

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


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from premium_users.models import PremiumUser
import json

@login_required(login_url='core:admin_login')
@require_http_methods(["GET"])
def api_admin_bulk_download(request):
    """
    ADMIN ONLY - Download ALL content for offline distribution.
    
    Returns:
    {
        "departments": [...],
        "courses": [...],
        "topics": [...],
        "premium_users": [...],
        "sync_timestamp": 1737244800
    }
    """
    # Get all departments
    departments = list(Department.objects.values('id', 'name'))
    
    # Get all courses (not deleted)
    courses = Course.objects.filter(is_deleted=False).prefetch_related('departments')
    courses_data = []
    for course in courses:
        courses_data.append({
            'id': course.id,
            'name': course.name,
            'year': course.year,
            'departments': [d.id for d in course.departments.all()],
            'created_at': int(course.created_at.timestamp()),
            'updated_at': int(course.updated_at.timestamp()),
        })
    
    # Get all topics (not deleted)
    topics = Topic.objects.filter(is_deleted=False).select_related('course')
    topics_data = []
    for topic in topics:
        topics_data.append({
            'id': topic.id,
            'course_id': topic.course.id,
            'title': topic.title,
            'page_range': topic.page_range,
            'refined_summary': topic.refined_summary,
            'raw_text': topic.raw_text,
            'is_premium': topic.is_premium,
            'difficulty_level': topic.difficulty_level,
            'order': topic.order,
            'created_at': int(topic.created_at.timestamp()),
            'updated_at': int(topic.updated_at.timestamp()),
        })
    
    # Get all active premium users
    premium_users = list(
        PremiumUser.objects.filter(is_active=True).values(
            'id', 'name', 'code', 'department_id'
        )
    )
    
    return JsonResponse({
        'departments': departments,
        'courses': courses_data,
        'topics': topics_data,
        'premium_users': premium_users,
        'sync_timestamp': int(timezone.now().timestamp()),
        'total_topics': len(topics_data),
        'total_users': len(premium_users),
    })


@login_required(login_url='core:admin_login')
@require_http_methods(["POST"])
def api_admin_upload_users(request):
    """
    ADMIN ONLY - Upload user registrations collected offline.
    
    Expects:
    {
        "users": [
            {"name": "John Doe", "code": "JD23", "department_id": 5},
            ...
        ]
    }
    
    Returns:
    {
        "created": 5,
        "duplicates": 2,
        "errors": []
    }
    """
    try:
        data = json.loads(request.body)
        users_data = data.get('users', [])
        
        created_count = 0
        duplicate_count = 0
        errors = []
        
        for user_data in users_data:
            try:
                name = user_data.get('name', '').strip()
                code = user_data.get('code', '').strip().upper()
                department_id = user_data.get('department_id')
                
                # Validate
                if not name or not code:
                    errors.append(f"Missing name or code: {user_data}")
                    continue
                
                if len(code) != 4:
                    errors.append(f"Invalid code length for {name}: {code}")
                    continue
                
                # Check if user already exists
                if PremiumUser.objects.filter(name=name, code=code).exists():
                    duplicate_count += 1
                    continue
                
                # Get department
                department = None
                if department_id:
                    try:
                        department = Department.objects.get(id=department_id)
                    except Department.DoesNotExist:
                        errors.append(f"Department {department_id} not found for {name}")
                        continue
                
                # Create user
                PremiumUser.objects.create(
                    name=name,
                    code=code,
                    department=department,
                    is_active=True
                )
                created_count += 1
                
            except Exception as e:
                errors.append(f"Error creating user {user_data}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'created': created_count,
            'duplicates': duplicate_count,
            'errors': errors,
            'total_processed': len(users_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


