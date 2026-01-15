
# ==================== views_functions/scan_views.py ====================
"""
Scanning views - Handle OCR scanning and topic creation from images
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import os
from django.conf import settings

from ..models import Course, Topic, Department
from ..utils.ocr import extract_text_from_image, extract_text_from_images_batch


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
        difficulty_level = request.POST.get('difficulty_level', 'medium')
        is_premium = (topic_type == 'premium')

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
            is_premium=is_premium,
            difficulty_level=difficulty_level
        )

        request.session.pop('extracted_text', None)
        request.session.pop('temp_image_count', None)

        if is_premium:
            messages.success(request, f"Premium topic '{topic_title}' ({difficulty_level}) saved!")
        else:
            messages.success(request, f"Community topic '{topic_title}' ({difficulty_level}) saved!")
        
        return render(request, 'scan/partials/save_success.html', {
            'topic': topic,
            'course': course,
            'is_premium': is_premium
        })

    return redirect('scan_new')

