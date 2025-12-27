from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q
from .models import Course, Topic, Department
from .utils.ocr import extract_text_from_image, extract_text_from_images_batch, test_ocr_connection
import os
from django.conf import settings
from premium_users.views import (
    filter_topics_for_user, 
    check_topic_access,
    get_active_premium_users_for_select
)

# ============= HOME =============
def home(request):
    """Main landing page with two options"""
    return render(request, 'scan/partials/home.html')


# ============= SCANNING =============
def scan_new(request):
    """Scan new pages interface"""
    return render(request, 'scan/partials/scan.html')

@csrf_exempt
def upload_and_extract(request):
    """Upload images and extract text via OCR (WITH BATCH PROCESSING)"""
    if request.method == 'POST' and request.FILES.getlist('images'):
        try:
            image_files = request.FILES.getlist('images')
            temp_paths = []
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            for idx, img in enumerate(image_files, 1):
                img_path = os.path.join(temp_dir, f'temp_{idx}_{img.name}')
                with open(img_path, 'wb+') as f:
                    for chunk in img.chunks():
                        f.write(chunk)
                temp_paths.append(img_path)
            
            if len(temp_paths) > 1:
                batch_results = extract_text_from_images_batch(temp_paths)
                all_text = ""
                for result in batch_results:
                    page_num = result['page']
                    text = result['text']
                    all_text += f"--- Page {page_num} ---\n{text}\n\n"
            else:
                text = extract_text_from_image(temp_paths[0])
                all_text = f"--- Page 1 ---\n{text}\n\n"
            
            for img_path in temp_paths:
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except Exception as e:
                    print(f"Warning: Could not delete {img_path}: {e}")
            
            try:
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass
            
            request.session['extracted_text'] = all_text
            request.session['temp_image_count'] = len(image_files)
            
            courses = Course.objects.filter(is_deleted=False)
            
            return render(request, 'scan/partials/save_form.html', {
                'extracted_text': all_text,
                'courses': courses,
                'page_count': len(image_files)
            })
            
        except Exception as e:
            return render(request, 'scan/partials/error.html', {
                'error': str(e)
            })
    
    return JsonResponse({'error': 'No images uploaded'}, status=400)


@csrf_exempt
def save_topic(request):
    """Save extracted text as a new topic."""
    if request.method == 'POST':
        raw_text = request.session.get('extracted_text')
        if not raw_text:
            messages.error(request, "No extracted text found. Please scan again.")
            return redirect('scan_new')

        course_option = request.POST.get('course_option')
        topic_title = request.POST.get('topic_title')
        page_range = request.POST.get('page_range', '')
        topic_type = request.POST.get('topic_type', 'community')
        is_premium = (topic_type == 'premium')

        print(f"[SAVE TOPIC] topic_type received: '{topic_type}'")
        print(f"[SAVE TOPIC] is_premium set to: {is_premium}")

        if course_option == 'new':
            course_name = request.POST.get('new_course_name')
            if not course_name:
                messages.error(request, "Course name is required.")
                return redirect('scan_new')
            course_subject = request.POST.get('new_course_subject', '')
            course = Course.objects.create(name=course_name)
            if course_subject:
                dept = Department.get_or_create_department(course_subject)
                if dept:
                    course.departments.add(dept)
        else:
            course_id = request.POST.get('existing_course')
            if not course_id:
                messages.error(request, "Please select a course.")
                return redirect('scan_new')
            course = get_object_or_404(Course, id=course_id, is_deleted=False)

        topic = Topic.objects.create(
            course=course,
            title=topic_title,
            raw_text=raw_text,
            page_range=page_range,
            order=course.topics.filter(is_deleted=False).count(),
            is_premium=is_premium
        )
        
        print(f"[SAVE TOPIC] Topic #{topic.id} created successfully")
        print(f"[SAVE TOPIC] Topic.is_premium = {topic.is_premium}")
        print(f"[SAVE TOPIC] Topic title: {topic.title}")

        request.session.pop('extracted_text', None)
        request.session.pop('temp_image_count', None)

        if is_premium:
            messages.success(request, f"Premium topic '{topic_title}' saved! Assign users in 'Send Premium Topics' page.")
        else:
            messages.success(request, f"Community topic '{topic_title}' saved!")
        
        return render(request, 'scan/partials/save_success.html', {
            'topic': topic,
            'course': course,
            'is_premium': is_premium
        })

    return redirect('scan_new')


# ============= LIBRARY =============
def library(request):
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


# ============= COURSE MANAGEMENT =============
def create_course(request):
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


def delete_topic(request, topic_id):
    """Soft delete a topic"""
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id=topic_id)
        course_id = topic.course.id
        topic.soft_delete()
        messages.success(request, f"Topic '{topic.title}' deleted successfully.")
        return redirect('course_detail', course_id=course_id)
    return redirect('library')


# ============= PUBLIC API (For Mobile App) =============
def api_departments(request):
    departments = Department.objects.all()
    return JsonResponse([{'id': d.id, 'name': d.name} for d in departments], safe=False)


def api_course_topics(request, course_id):
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


def manage_topic_assignments(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    if not topic.is_premium:
        messages.error(request, "This is a community topic - no user assignments needed.")
        return redirect('topic_detail', topic_id=topic.id)

    from premium_users.models import PremiumUser
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


def api_topic_detail(request, topic_id):
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


# ============= MANAGE PREMIUM TOPICS =============
def manage_premium_topics(request):
    """Admin page to manage all premium topics."""
    from premium_users.models import PremiumUser

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


# ============= UTILITIES =============
def ocr_status(request):
    is_healthy, message = test_ocr_connection()
    return JsonResponse({'healthy': is_healthy, 'message': message})