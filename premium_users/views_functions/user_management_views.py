# ==================== VIEW: user_management_views.py ====================
"""
User management views - CRUD operations for premium users
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from ..models import PremiumUser
from scan.models import Department


def manage_premium_users(request):
    """
    Main page to view/edit/delete premium users.
    """
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    department_filter = request.GET.get('department', 'all')

    users = PremiumUser.objects.select_related('department').all()

    if search:
        users = users.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    if department_filter != 'all':
        if department_filter == 'none':
            users = users.filter(department__isnull=True)
        else:
            users = users.filter(department_id=department_filter)

    users = users.order_by('-created_at')

    all_departments = Department.objects.all().order_by('name')

    context = {
        'users': users,
        'search': search,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'all_departments': all_departments,
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
    all_departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        department_id = request.POST.get('department')

        # Validation
        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.filter(code=code).exists():
            error = "This code already exists."

        # Validate department
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                error = "Invalid department selected."

        if not error:
            PremiumUser.objects.create(
                name=name,
                code=code,
                department=department,
                is_active=True
            )
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/add_user.html', {
        'error': error,
        'all_departments': all_departments
    })


def edit_premium_user(request, user_id):
    """Edit an existing premium user"""
    user = get_object_or_404(PremiumUser, id=user_id)
    error = None
    all_departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        department_id = request.POST.get('department')

        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.exclude(id=user.id).filter(code=code).exists():
            error = "This code already exists."

        # Validate department
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                error = "Invalid department selected."

        if not error:
            user.name = name
            user.code = code
            user.department = department
            user.save()
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/edit_user.html', {
        'user': user,
        'error': error,
        'all_departments': all_departments
    })


@csrf_exempt
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    if request.method == 'POST':
        user = get_object_or_404(PremiumUser, id=user_id)
        user.is_active = not user.is_active
        user.save()
    return redirect('premium_users:manage_users')


@csrf_exempt
def delete_premium_user(request, user_id):
    """Delete a premium user"""
    if request.method == 'POST':
        user = get_object_or_404(PremiumUser, id=user_id)
        user.delete()
    return redirect('premium_users:manage_users')

