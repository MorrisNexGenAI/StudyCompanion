from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Course, Topic, Department
from .utils.ocr import extract_text_from_image, extract_text_from_images_batch, test_ocr_connection
import os
from django.conf import settings

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
            # Process all uploaded images
            image_files = request.FILES.getlist('images')
            
            # Save images temporarily
            temp_paths = []
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            for idx, img in enumerate(image_files, 1):
                img_path = os.path.join(temp_dir, f'temp_{idx}_{img.name}')
                with open(img_path, 'wb+') as f:
                    for chunk in img.chunks():
                        f.write(chunk)
                temp_paths.append(img_path)
            
            # Batch processing for multiple images
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
            
            # Auto-delete temporary images
            for img_path in temp_paths:
                try:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except Exception as e:
                    print(f"Warning: Could not delete {img_path}: {e}")
            
            # Clean up temp directory if empty
            try:
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass
            
            # Store extracted text in session
            request.session['extracted_text'] = all_text
            request.session['temp_image_count'] = len(image_files)
            
            # Get all courses for dropdown
            courses = Course.objects.all()
            
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
    """Save extracted text as a new topic"""
    if request.method == 'POST':
        try:
            # Get form data
            course_option = request.POST.get('course_option')
            topic_title = request.POST.get('topic_title')
            page_range = request.POST.get('page_range', '')
            
            # Get extracted text from session
            raw_text = request.session.get('extracted_text', '')
            
            if not raw_text:
                return JsonResponse({'error': 'No extracted text found. Please scan again.'}, status=400)
            
            # Handle course selection
            if course_option == 'new':
                course_name = request.POST.get('new_course_name')
                course_subject = request.POST.get('new_course_subject', '')
                course = Course.objects.create(name=course_name)
                
                # Handle department (legacy support)
                if course_subject:
                    dept = Department.get_or_create_department(course_subject)
                    if dept:
                        course.departments.add(dept)
            else:
                course_id = request.POST.get('existing_course')
                course = get_object_or_404(Course, id=course_id)
            
            # Create topic
            topic = Topic.objects.create(
                course=course,
                title=topic_title,
                raw_text=raw_text,
                page_range=page_range,
                order=course.topics.count()
            )
            
            # Clear session
            request.session.pop('extracted_text', None)
            request.session.pop('temp_image_count', None)
            
            return render(request, 'scan/partials/save_success.html', {
                'topic': topic,
                'course': course
            })
            
        except Exception as e:
            return render(request, 'scan/partials/error.html', {
                'error': str(e)
            })
    
    return redirect('scan_new')


# ============= LIBRARY =============
def library(request):
    """Show all courses"""
    courses = Course.objects.prefetch_related('departments').all()
    return render(request, 'scan/partials/library.html', {
        'courses': courses
    })


def course_detail(request, course_id):
    """Show all topics in a course"""
    course = get_object_or_404(Course.objects.prefetch_related('departments'), id=course_id)
    topics = course.topics.all()
    return render(request, 'scan/partials/course_detail.html', {
        'course': course,
        'topics': topics
    })


def course_full_summary(request, course_id):
    """Show combined refined text for entire course"""
    course = get_object_or_404(Course.objects.prefetch_related('departments'), id=course_id)
    full_text = course.get_full_refined_text()
    return render(request, 'scan/partials/full_summary.html', {
        'course': course,
        'full_text': full_text
    })


def topic_detail(request, topic_id):
    """View single topic with raw text"""
    topic = get_object_or_404(Topic, id=topic_id)
    return render(request, 'scan/partials/topic_detail.html', {
        'topic': topic
    })


@csrf_exempt
def edit_refined_summary(request, topic_id):
    """Add or edit refined summary"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    if request.method == 'POST':
        refined_text = request.POST.get('refined_summary', '')
        topic.refined_summary = refined_text
        topic.save()
        return redirect('topic_detail', topic_id=topic.id)
    
    return render(request, 'scan/partials/edit_refined.html', {
        'topic': topic
    })


# ============= COURSE MANAGEMENT =============
def create_course(request):
    """Create new course with multiple departments"""
    if request.method == 'POST':
        # Create course
        course = Course.objects.create(
            name=request.POST.get('name'),
            year=request.POST.get('year', ''),
            description=request.POST.get('description', '')
        )
        
        # Handle multiple departments
        department_ids = request.POST.getlist('departments')
        if department_ids:
            course.departments.set(department_ids)
        
        return redirect('course_detail', course_id=course.id)
    
    # GET request - show form
    all_departments = Department.objects.all()
    return render(request, 'scan/partials/create_course.html', {
        'all_departments': all_departments
    })


def delete_course(request, course_id):
    """Delete a course and all its topics"""
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        return redirect('library')
    return redirect('library')


def delete_topic(request, topic_id):
    """Delete a topic"""
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id=topic_id)
        course_id = topic.course.id
        topic.delete()
        return redirect('course_detail', course_id=course_id)
    return redirect('library')


# ============= PUBLIC API (For Mobile App) =============

def api_departments(request):
    """GET /api/departments/ - List all departments"""
    departments = Department.objects.all()
    data = [{'id': d.id, 'name': d.name} for d in departments]
    return JsonResponse(data, safe=False)


def api_department_courses(request, dept_id):
    """GET /api/departments/<int:dept_id>/courses/ - List courses in department"""
    department = get_object_or_404(Department, id=dept_id)
    courses = department.courses.prefetch_related('departments').all()
    
    data = []
    for course in courses:
        data.append({
            'id': course.id,
            'name': course.name,
            'year': course.year,
            'departments': [{'id': d.id, 'name': d.name} for d in course.departments.all()],
            'topic_count': course.get_total_topics(),
            'refined_count': course.get_refined_count(),
        })
    
    return JsonResponse(data, safe=False)


def api_course_topics(request, course_id):
    """GET /api/courses/<int:course_id>/topics/ - List topics metadata (no full text)"""
    course = get_object_or_404(Course, id=course_id)
    topics = course.topics.all()
    
    data = []
    for topic in topics:
        data.append({
            'id': topic.id,
            'title': topic.title,
            'page_range': topic.page_range,
            'updated_at': int(topic.updated_at.timestamp()),
            'is_refined': topic.is_refined(),
        })
    
    return JsonResponse(data, safe=False)


def api_topic_detail(request, topic_id):
    """GET /api/topics/<int:topic_id>/ - Get full topic with refined summary"""
    topic = get_object_or_404(Topic.objects.select_related('course').prefetch_related('course__departments'), id=topic_id)
    
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
    }
    
    return JsonResponse(data)


# ============= UTILITIES =============
def ocr_status(request):
    """Check if OCR engine is running"""
    is_healthy, message = test_ocr_connection()
    return JsonResponse({
        'healthy': is_healthy,
        'message': message
    })
