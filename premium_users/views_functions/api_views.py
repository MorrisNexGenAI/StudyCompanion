# ==================== VIEW: api_views.py ====================
"""
API views - REST endpoints for mobile/React apps
Updated for Phase 5: Department + Year filtering
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from ..models import PremiumUser
from scan.models import Topic, Department, Course


@csrf_exempt
def register_or_login(request):
    """API endpoint for user registration/login with department selection"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import json
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        code = data.get('code', '').strip().upper()
        department_id = data.get('department_id')  # REQUIRED NOW

        # Validation
        if not name or not code:
            return JsonResponse({'error': 'Name and code are required'}, status=400)

        if len(code) != 4 or not code.isalnum():
            return JsonResponse({'error': 'Invalid code format'}, status=400)

        # Validate department (REQUIRED)
        if not department_id:
            return JsonResponse({'error': 'Department selection is required'}, status=400)

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Invalid department selected'}, status=400)

        # Check exact match (LOGIN CASE)
        user = PremiumUser.objects.filter(
            name__iexact=name,
            code=code
        ).first()

        if user:
            if not user.is_active:
                return JsonResponse({'error': 'Account is inactive'}, status=403)

            # Update department if provided and different
            if user.department != department:
                user.department = department
                user.save(update_fields=['department', 'updated_at'])

            return JsonResponse({
                'user_id': user.id,
                'name': user.name,
                'code': user.code,
                'department_id': user.department.id,
                'department_name': user.department.name,
                'is_new': False
            })

        # Check partial conflicts (SECURITY)
        if PremiumUser.objects.filter(code=code).exists():
            return JsonResponse({
                'error': 'This code is already linked to another user'
            }, status=403)

        if PremiumUser.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'error': 'This name is already linked to another code'
            }, status=403)

        # CREATE (FIRST TIME)
        user = PremiumUser.objects.create(
            name=name,
            code=code,
            department=department,
            is_active=True
        )

        return JsonResponse({
            'user_id': user.id,
            'name': user.name,
            'code': user.code,
            'department_id': user.department.id,
            'department_name': user.department.name,
            'is_new': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_accessible_topics(request, user_id):
    """
    DEPRECATED - Use get_courses_by_department_and_year instead
    Kept for backward compatibility
    """
    user = get_object_or_404(PremiumUser, id=user_id, is_active=True)

    if not user.department:
        return JsonResponse({
            'user': {
                'id': user.id,
                'name': user.name,
                'code': user.code,
                'department': None
            },
            'topics': [],
            'message': 'Please select a department to view topics'
        })

    # Get all topics from courses in user's department
    department_topics = Topic.objects.filter(
        course__departments=user.department,
        is_deleted=False
    )

    # Filter by access rules
    community_topics = department_topics.filter(is_premium=False)
    premium_topics = department_topics.filter(
        is_premium=True,
        premium_users=user
    )

    topics = (community_topics | premium_topics).distinct().order_by('-created_at')

    data = [{
        'id': t.id,
        'title': t.title,
        'is_premium': t.is_premium,
        'course_id': t.course.id,
        'course_name': t.course.name,
        'page_range': t.page_range,
    } for t in topics]

    return JsonResponse({
        'user': {
            'id': user.id,
            'name': user.name,
            'code': user.code,
            'department_id': user.department.id,
            'department_name': user.department.name
        },
        'topics': data
    })


def get_user_department(request, user_id):
    """
    NEW ENDPOINT: Get user's department only
    Used after login to show only user's department
    """
    user = get_object_or_404(PremiumUser, id=user_id, is_active=True)

    if not user.department:
        return JsonResponse({
            'error': 'User has no department assigned'
        }, status=400)

    return JsonResponse({
        'user': {
            'id': user.id,
            'name': user.name,
            'code': user.code,
        },
        'department': {
            'id': user.department.id,
            'name': user.department.name,
        }
    })


def get_courses_by_department_and_year(request, department_id):
    """
    NEW ENDPOINT: Get courses filtered by department AND academic year
    Query param: ?year=2024/2025 (optional)
    """
    try:
        # Get user_id from query params (added by interceptor)
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)

        # Verify user access
        user = get_object_or_404(PremiumUser, id=user_id, is_active=True)
        
        # Verify user belongs to this department
        if not user.department or user.department.id != int(department_id):
            return JsonResponse({'error': 'Access denied to this department'}, status=403)

        # Get year filter (optional)
        year = request.GET.get('year')

        # Base query: courses in this department
        courses = Course.objects.filter(
            departments__id=department_id,
            is_deleted=False
        ).distinct()

        # Apply year filter if provided
        if year:
            courses = courses.filter(year=year)

        # Get all available years for this department
        available_years = Course.objects.filter(
            departments__id=department_id,
            is_deleted=False
        ).values_list('year', flat=True).distinct().order_by('-year')

        # Serialize courses
        courses_data = []
        for course in courses:
            # Count topics (community + premium assigned to user)
            total_topics = Topic.objects.filter(
                course=course,
                is_deleted=False
            ).filter(
                Q(is_premium=False) |  # Community topics
                Q(is_premium=True, premium_users=user)  # Premium topics assigned to user
            ).distinct().count()

            # Count refined topics
            refined_topics = Topic.objects.filter(
                course=course,
                is_deleted=False,
                refined_summary__isnull=False
            ).exclude(refined_summary='').filter(
                Q(is_premium=False) |
                Q(is_premium=True, premium_users=user)
            ).distinct().count()

            courses_data.append({
                'id': course.id,
                'name': course.name,
                'year': course.year,
                'departments': [{'id': d.id, 'name': d.name} for d in course.departments.all()],
                'topic_count': total_topics,
                'refined_count': refined_topics,
            })

        return JsonResponse({
            'courses': courses_data,
            'available_years': list(available_years),
            'current_year': year,
            'department': {
                'id': user.department.id,
                'name': user.department.name,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_topics_by_course(request, course_id):
    """
    Get topics for a course (filtered by user's department access)
    """
    try:
        # Get user_id from query params
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)

        user = get_object_or_404(PremiumUser, id=user_id, is_active=True)
        course = get_object_or_404(Course, id=course_id, is_deleted=False)

        # Verify user's department has access to this course
        if user.department not in course.departments.all():
            return JsonResponse({'error': 'Access denied to this course'}, status=403)

        # Get accessible topics
        topics = Topic.objects.filter(
            course=course,
            is_deleted=False
        ).filter(
            Q(is_premium=False) |  # Community topics
            Q(is_premium=True, premium_users=user)  # Premium topics
        ).distinct().order_by('-created_at')

        data = [{
            'id': t.id,
            'title': t.title,
            'page_range': t.page_range,
            'updated_at': int(t.updated_at.timestamp()),
            'is_refined': bool(t.refined_summary and t.refined_summary.strip()),
            'is_premium': t.is_premium,
        } for t in topics]

        return JsonResponse({
            'topics': data,
            'course': {
                'id': course.id,
                'name': course.name,
                'year': course.year,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_topic_full(request, topic_id):
    """
    Get full topic content (filtered by user access)
    """
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)

        user = get_object_or_404(PremiumUser, id=user_id, is_active=True)
        topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)

        # Check access
        if topic.is_premium and user not in topic.premium_users.all():
            return JsonResponse({'error': 'Access denied to premium topic'}, status=403)

        # Check department access
        if user.department not in topic.course.departments.all():
            return JsonResponse({'error': 'Access denied to this department'}, status=403)

        return JsonResponse({
            'id': topic.id,
            'title': topic.title,
            'page_range': topic.page_range,
            'refined_summary': topic.refined_summary or '',
            'raw_text': topic.raw_text or '',
            'course_name': topic.course.name,
            'course_year': topic.course.year,
            'departments': [d.name for d in topic.course.departments.all()],
            'updated_at': int(topic.updated_at.timestamp()),
            'created_at': int(topic.created_at.timestamp()),
            'is_premium': topic.is_premium,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_departments_list(request):
    """API endpoint to get all available departments for registration"""
    departments = Department.objects.all().order_by('name')
    
    data = [{
        'id': d.id,
        'name': d.name
    } for d in departments]
    
    return JsonResponse({
        'departments': data
    })


def get_available_years(request, department_id):
    """
    NEW ENDPOINT: Get all available academic years for a department
    """
    try:
        department = get_object_or_404(Department, id=department_id)
        
        years = Course.objects.filter(
            departments=department,
            is_deleted=False
        ).values_list('year', flat=True).distinct().order_by('-year')

        return JsonResponse({
            'department_id': department.id,
            'department_name': department.name,
            'years': list(years)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

