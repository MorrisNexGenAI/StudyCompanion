# ==================== views_functions/text_input_views.py ====================
"""
Text input views - Direct text input bypassing OCR
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from ..models import Course, Topic


def text_input_page(request):
    """Page for direct text input (bypassing OCR)"""
    courses = Course.objects.filter(is_deleted=False)
    return render(request, 'scan/partials/text_input.html', {'courses': courses})


def process_text_input(request):
    """Process direct text input and create topic"""
    if request.method == 'POST':
        try:
            topic_title = request.POST.get('topic_title', '').strip()
            raw_text = request.POST.get('raw_text', '').strip()
            page_range = request.POST.get('page_range', '').strip()
            topic_type = request.POST.get('topic_type', 'community')
            difficulty_level = request.POST.get('difficulty_level', 'medium')
            course_option = request.POST.get('course_option', 'existing')
            
            if not topic_title or not raw_text:
                messages.error(request, "Topic title and text content are required")
                return redirect('text_input')
            
            if course_option == 'existing':
                existing_course_id = request.POST.get('existing_course')
                if not existing_course_id:
                    messages.error(request, "Please select a course")
                    return redirect('text_input')
                course = Course.objects.get(id=existing_course_id, is_deleted=False)
            else:
                new_course_name = request.POST.get('new_course_name', '').strip()
                if not new_course_name:
                    messages.error(request, "New course name is required")
                    return redirect('text_input')
                course = Course.objects.create(name=new_course_name)
            
            metadata = f"[Source: Direct Text Input | Added: {timezone.now().strftime('%Y-%m-%d %H:%M')}]\n\n"
            full_text = metadata + raw_text
            
            topic = Topic.objects.create(
                course=course,
                title=topic_title,
                raw_text=full_text,
                page_range=page_range,
                order=course.topics.filter(is_deleted=False).count(),
                is_premium=(topic_type == 'premium'),
                difficulty_level=difficulty_level
            )
            messages.success(request, f"Topic '{topic_title}' ({difficulty_level}) created successfully!")
            return redirect('topic_detail', topic_id=topic.id)
        except Exception as e:
            messages.error(request, f"Error creating topic: {str(e)}")
            return redirect('text_input')
    
    return redirect('text_input')


