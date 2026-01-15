# ==================== views_functions/course_management_views.py ====================
"""
Course management views - Create and delete courses
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Course, Department


def create_course(request):
    """Create a new course"""
    if request.method == 'POST':
        course = Course.objects.create(
            name=request.POST.get('name'),
            year=request.POST.get('year', ''),
            description=request.POST.get('description', '')
        )
        department_ids = request.POST.getlist('departments')
        if department_ids:
            course.departments.set(department_ids)
        return redirect('course_detail', course_id=course.id)
    
    all_departments = Department.objects.all()
    return render(request, 'scan/partials/create_course.html', {'all_departments': all_departments})


def delete_course(request, course_id):
    """Soft delete a course"""
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.soft_delete()
        messages.success(request, f"Course '{course.name}' deleted successfully.")
        return redirect('library')
    return redirect('library')
