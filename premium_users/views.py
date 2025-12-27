from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import PremiumUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from scan.models import Topic


# ============= TEMPLATE VIEWS (Custom Admin UI) =============

def manage_premium_users(request):
    """
    Main page to view/edit/delete premium users.
    """
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')

    users = PremiumUser.objects.all()

    if search:
        users = users.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    users = users.order_by('-created_at')

    context = {
        'users': users,
        'search': search,
        'status_filter': status_filter,
        'total_count': PremiumUser.objects.count(),
        'active_count': PremiumUser.objects.filter(is_active=True).count(),
        'inactive_count': PremiumUser.objects.filter(is_active=False).count(),
    }

    return render(request, 'premium_users/manage_users.html', context)


def add_premium_user(request):
    """
    Create a new premium user (custom page).
    """
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()

        # Validation
        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.filter(code=code).exists():
            error = "This code already exists."

        if not error:
            PremiumUser.objects.create(
                name=name,
                code=code,
                is_active=True
            )
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/add_user.html', {
        'error': error
    })


def edit_premium_user(request, user_id):
    user = get_object_or_404(PremiumUser, id=user_id)
    error = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()

        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.exclude(id=user.id).filter(code=code).exists():
            error = "This code already exists."

        if not error:
            user.name = name
            user.code = code
            user.save()
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/edit_user.html', {
        'user': user,
        'error': error
    })


@csrf_exempt
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(PremiumUser, id=user_id)
        user.is_active = not user.is_active
        user.save()
    return redirect('premium_users:manage_users')


@csrf_exempt
def delete_premium_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(PremiumUser, id=user_id)
        user.delete()
    return redirect('premium_users:manage_users')


# ============= API ENDPOINTS (React / Mobile) =============
@csrf_exempt
def register_or_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import json
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        code = data.get('code', '').strip().upper()

        # Validation
        if not name or not code:
            return JsonResponse({'error': 'Name and code are required'}, status=400)

        if len(code) != 4 or not code.isalnum():
            return JsonResponse({'error': 'Invalid code format'}, status=400)

        # Check exact match (LOGIN CASE)
        user = PremiumUser.objects.filter(
            name__iexact=name,
            code=code
        ).first()

        if user:
            if not user.is_active:
                return JsonResponse({'error': 'Account is inactive'}, status=403)

            return JsonResponse({
                'user_id': user.id,
                'name': user.name,
                'code': user.code,
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
            is_active=True
        )

        return JsonResponse({
            'user_id': user.id,
            'name': user.name,
            'code': user.code,
            'is_new': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_accessible_topics(request, user_id):
    """
    CRITICAL FIX: Returns ONLY topics this specific user can access.
    - Community topics (everyone can see)
    - Premium topics where this user is EXPLICITLY assigned
    """
    user = get_object_or_404(PremiumUser, id=user_id, is_active=True)

    # Get community topics (available to everyone)
    community_topics = Topic.objects.filter(is_premium=False)
    
    # Get ONLY premium topics where THIS user is explicitly assigned
    premium_topics = user.accessible_topics.filter(is_premium=True)

    # Combine both sets
    topics = community_topics.union(premium_topics).order_by('-created_at')

    data = [{
        'id': t.id,
        'title': t.title,
        'is_premium': t.is_premium,
        'course_id': t.course.id,
        'course_name': t.course.name
    } for t in topics]

    return JsonResponse({
        'user': {
            'id': user.id,
            'name': user.name,
            'code': user.code
        },
        'topics': data
    })


# ============= HELPERS (used by scan app) =============
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
@login_required
def delete_premium_topic(request, topic_id):
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

def get_active_premium_users_for_select():
    """Get all active premium users (for assignment dropdowns)"""
    return PremiumUser.objects.filter(is_active=True).order_by('name')