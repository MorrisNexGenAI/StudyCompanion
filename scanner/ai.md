this is my models:
from django.db import models
from core.models import BaseModel


class Department(BaseModel):
    """Represents a department/subject area (e.g., Health Science, Engineering)"""
    name = models.CharField(max_length=200, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_department(cls, name):
        """Get existing or create new department (case-insensitive)"""
        if not name or not name.strip():
            return None
        name = name.strip()
        dept, created = cls.objects.get_or_create(name__iexact=name, defaults={'name': name})
        return dept


class Course(BaseModel):
    """Represents a course (e.g., BIO 202, CHEM 101)"""
    name = models.CharField(max_length=200)
    departments = models.ManyToManyField(Department, blank=True, related_name='courses')
    year = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total_topics(self):
        return self.topics.count()
    
    def get_refined_count(self):
        return self.topics.filter(refined_summary__isnull=False).exclude(refined_summary='').count()
    
    def get_departments_display(self):
        """Return comma-separated department names"""
        return ", ".join([d.name for d in self.departments.all()])
    
    def get_full_refined_text(self):
        """Combine all refined summaries in order"""
        topics = self.topics.filter(
            refined_summary__isnull=False
        ).exclude(refined_summary='').order_by('order', 'created_at')
        
        # Header
        full_text = f"{self.name}\n"
        dept_display = self.get_departments_display()
        if dept_display:
            full_text += f"{dept_display}\n"
        if self.year:
            full_text += f"Year: {self.year}\n"
        full_text += "=" * 50 + "\n\n"
        
        # Topics
        for topic in topics:
            full_text += f"📚 {topic.title}\n"
            if topic.page_range:
                full_text += f"Pages: {topic.page_range}\n"
            full_text += "\n" + topic.refined_summary + "\n\n"
            full_text += "-" * 50 + "\n\n"
        
        return full_text


class Topic(BaseModel):
    """Represents a topic within a course (e.g., 'Cell Structure - Pages 1-3')"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=300)
    raw_text = models.TextField(blank=True)
    refined_summary = models.TextField(blank=True)
    page_range = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['course', 'order', 'created_at']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    def is_refined(self):
        """Check if topic has refined summary"""
        return bool(self.refined_summary and self.refined_summary.strip())
    
    def get_status(self):
        """Get status badge"""
        return "✓ Refined" if self.is_refined() else "✏ Raw Only"


we are going to create new model called AIModel.py for the ai logic.

this is my view:
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

we wil also create aiview.py too for the ai views.
the ai logic will be in this file: [text](../scan/utils/ai.py)
and the ai text will be returned on the screen as refine.


see my htmls:
edit refined:
{% extends "scan/partials/base.html" %}

{% block content %}
<div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <p class="text-sm text-gray-600 mb-1">{{ topic.course.name }}</p>
            <h1 class="text-2xl font-bold text-indigo-600">{% if topic.refined_summary %}Edit{% else %}Add{% endif %} Refined Summary</h1>
            <p class="text-gray-600">{{ topic.title }}</p>
        </div>
        <a href="{% url 'topic_detail' topic.id %}" class="text-gray-600 hover:text-gray-800">← Cancel</a>
    </div>
    
    <div class="bg-blue-50 border-2 border-blue-300 rounded-xl p-4 mb-6">
        <h3 class="font-bold text-blue-800 mb-2">📝 How to Add Refined Summary:</h3>
        <ol class="text-sm text-blue-700 space-y-1">
            <li>1. Go back and copy your raw text</li>
            <li>2. Open ChatGPT (click button below)</li>
            <li>3. Paste and ask: "Summarize with key points and questions"</li>
            <li>4. Copy ChatGPT's response</li>
            <li>5. Paste here and save</li>
        </ol>
        <a href="https://chat.openai.com" target="_blank" 
           class="inline-block mt-3 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm">
            🔗 Open ChatGPT
        </a>
    </div>
    
    <form method="POST" action="{% url 'edit_refined_summary' topic.id %}">
        {% csrf_token %}
        
        <div class="mb-4">
            <label class="block text-sm font-bold mb-2">Refined Summary from ChatGPT</label>
            <textarea name="refined_summary" rows="20" 
                      class="w-full p-4 border-2 border-gray-300 rounded-lg font-mono text-sm"
                      placeholder="Paste ChatGPT summary here...">{{ topic.refined_summary }}</textarea>
        </div>
        
        <div class="flex gap-3">
            <button type="submit" class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg text-lg">
                💾 Save
            </button>
            <a href="{% url 'topic_detail' topic.id %}" 
               class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-4 px-6 rounded-lg">
                Cancel
            </a>
        </div>
    </form>
</div>
{% endblock %}
path:
/home/morris/Desktop/scannerAi/scanner/scan/templates/scan/partials/edit_refined.html
i'm only sharing these files so you can figure out what we should do.
full summary:
{% extends "scan/partials/base.html" %}

{% block content %}
<div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h1 class="text-3xl font-bold text-indigo-600">{{ course.name }} - Full Summary</h1>
            
            <!-- Display Departments -->
            {% if course.departments.all %}
            <div class="flex flex-wrap gap-2 mt-2">
                {% for dept in course.departments.all %}
                <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                    {{ dept.name }}
                </span>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if course.year %}
            <p class="text-gray-600 mt-1">📅 {{ course.year }}</p>
            {% endif %}
        </div>
        <a href="{% url 'course_detail' course.id %}" class="text-gray-600 hover:text-gray-800">← Back</a>
    </div>
    
    <div class="grid md:grid-cols-3 gap-3 mb-6">
        <button onclick="copyFullSummary()" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition">
            📋 Copy All
        </button>
        <button onclick="window.print()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition">
            🖨️ Print
        </button>
        <button onclick="downloadText()" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition">
            💾 Download
        </button>
    </div>
    
    <div class="bg-green-50 border-2 border-green-300 rounded-xl p-4 mb-6">
        <p class="text-sm text-green-800">
            <strong>✓ Ready!</strong> Combines {{ course.get_refined_count }} refined topic(s). Copy and paste into Word.
        </p>
    </div>
    
    <div id="summaryContent" class="bg-white border-2 border-gray-200 rounded-xl p-6">
        <pre class="whitespace-pre-wrap font-sans text-sm leading-relaxed">{{ full_text }}</pre>
    </div>
    
    {% if course.get_refined_count == 0 %}
    <div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6 text-center mt-6">
        <p class="text-yellow-800 mb-3">No refined summaries yet</p>
        <a href="{% url 'course_detail' course.id %}" 
           class="inline-block bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-6 rounded-lg transition">
            Go Back
        </a>
    </div>
    {% endif %}
</div>

<textarea id="fullText" class="hidden">{{ full_text }}</textarea>

<script>
function copyFullSummary() {
    const text = document.getElementById('fullText');
    text.classList.remove('hidden');
    text.select();
    document.execCommand('copy');
    text.classList.add('hidden');
    alert('✓ Full summary copied! Paste into Word.');
}

function downloadText() {
    const text = document.getElementById('fullText').value;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '{{ course.name|slugify }}_summary.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
</script>
{% endblock %}

edit_refined:
{% extends "scan/partials/base.html" %}

{% block content %}
<div class="bg-white rounded-2xl shadow-xl p-8">
    <div class="flex items-center justify-between mb-6">
        <div>
            <p class="text-sm text-gray-600 mb-1">{{ topic.course.name }}</p>
            <h1 class="text-2xl font-bold text-indigo-600">{% if topic.refined_summary %}Edit{% else %}Add{% endif %} Refined Summary</h1>
            <p class="text-gray-600">{{ topic.title }}</p>
        </div>
        <a href="{% url 'topic_detail' topic.id %}" class="text-gray-600 hover:text-gray-800">← Cancel</a>
    </div>
    
    <div class="bg-blue-50 border-2 border-blue-300 rounded-xl p-4 mb-6">
        <h3 class="font-bold text-blue-800 mb-2">📝 How to Add Refined Summary:</h3>
        <ol class="text-sm text-blue-700 space-y-1">
            <li>1. Go back and copy your raw text</li>
            <li>2. Open ChatGPT (click button below)</li>
            <li>3. Paste and ask: "Summarize with key points and questions"</li>
            <li>4. Copy ChatGPT's response</li>
            <li>5. Paste here and save</li>
        </ol>
        <a href="https://chat.openai.com" target="_blank" 
           class="inline-block mt-3 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm">
            🔗 Open ChatGPT
        </a>
    </div>
    
    <form method="POST" action="{% url 'edit_refined_summary' topic.id %}">
        {% csrf_token %}
        
        <div class="mb-4">
            <label class="block text-sm font-bold mb-2">Refined Summary from ChatGPT</label>
            <textarea name="refined_summary" rows="20" 
                      class="w-full p-4 border-2 border-gray-300 rounded-lg font-mono text-sm"
                      placeholder="Paste ChatGPT summary here...">{{ topic.refined_summary }}</textarea>
        </div>
        
        <div class="flex gap-3">
            <button type="submit" class="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg text-lg">
                💾 Save
            </button>
            <a href="{% url 'topic_detail' topic.id %}" 
               class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-4 px-6 rounded-lg">
                Cancel
            </a>
        </div>
    </form>
</div>
{% endblock %}

i have more but, i think these can be

documentation:
# Phase 1: Django Backend Migration

## Overview
Migrated from single `subject` CharField to many-to-many `departments` relationship to support courses with multiple departments.

---

## Changes Made

### 1. Models (`scan/models.py`)

#### New Model: Department
```python
class Department(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    
    @classmethod
    def get_or_create_department(cls, name):
        # Case-insensitive lookup
        dept, created = cls.objects.get_or_create(
            name__iexact=name, 
            defaults={'name': name}
        )
        return dept
```

#### Updated Model: Course
**Removed:**
- `subject = models.CharField(max_length=200, blank=True)`

**Added:**
- `departments = models.ManyToManyField(Department, blank=True, related_name='courses')`
- `get_departments_display()` - Returns comma-separated department names
- Updated `get_full_refined_text()` - Includes departments in output

#### Model: Topic
- No changes (still references Course via ForeignKey)

---

### 2. Database Migrations

#### Created Tables:
- `scan_department` - Stores department names
- `scan_course_departments` - Many-to-many relationship table

#### Migration Strategy:
1. Deleted old database (`db.sqlite3`)
2. Deleted all migration files
3. Created fresh migrations: `python manage.py makemigrations`
4. Applied migrations: `python manage.py migrate`

---

### 3. Views (`scan/views.py`)

#### New API Endpoints (4 total):

**1. List Departments**
```python
GET /api/departments/
Response: [{"id": 1, "name": "Health Science"}, ...]
```

**2. Courses by Department**
```python
GET /api/departments/<dept_id>/courses/
Response: [{
    "id": 1,
    "name": "BIO 202",
    "year": "2024",
    "departments": [{"id": 1, "name": "Health Science"}],
    "topic_count": 5,
    "refined_count": 3
}, ...]
```

**3. Topics by Course (Metadata Only)**
```python
GET /api/courses/<course_id>/topics/
Response: [{
    "id": 1,
    "title": "Cell Division",
    "page_range": "Pages 1-5",
    "updated_at": 1703001234,
    "is_refined": true
}, ...]
```

**4. Full Topic with Content**
```python
GET /api/topics/<topic_id>/
Response: {
    "id": 1,
    "title": "Cell Division",
    "page_range": "Pages 1-5",
    "refined_summary": "...",
    "raw_text": "...",
    "course_name": "BIO 202",
    "course_year": "2024",
    "departments": ["Health Science"],
    "updated_at": 1703001234,
    "created_at": 1702995000
}
```

#### Updated Existing Views:
- `create_course()` - Now handles `POST.getlist('departments')`
- `library()` - Added `prefetch_related('departments')` for performance
- `course_detail()` - Added department prefetch
- `course_full_summary()` - Added department prefetch

---

### 4. URLs (`scan/urls.py`)

**Added API Routes:**
```python
path('api/departments/', views.api_departments),
path('api/departments/<int:dept_id>/courses/', views.api_department_courses),
path('api/courses/<int:course_id>/topics/', views.api_course_topics),
path('api/topics/<int:topic_id>/', views.api_topic_detail),
```

---

### 5. Templates

#### `create_course.html`
**Changed:**
- Replaced single text input with multi-select dropdown
- Added Choices.js library for enhanced UX
- Searchable department selection with tag removal

**Before:**
```html
<input type="text" name="subject" placeholder="e.g., Health Science">
```

**After:**
```html
<select name="departments" id="departmentSelect" multiple>
  {% for dept in all_departments %}
  <option value="{{ dept.id }}">{{ dept.name }}</option>
  {% endfor %}
</select>
<script src="https://cdn.jsdelivr.net/npm/choices.js/..."></script>
```

#### `course_detail.html`
**Changed:**
- Display departments as purple badge chips
- Show year separately
- Maintain all existing functionality

**Before:**
```html
{% if course.subject %}
<p class="text-gray-600">{{ course.subject }}</p>
{% endif %}
```

**After:**
```html
{% if course.departments.all %}
<div class="flex flex-wrap gap-2 mt-2">
  {% for dept in course.departments.all %}
  <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
    {{ dept.name }}
  </span>
  {% endfor %}
</div>
{% endif %}
```

#### `library.html`
**Changed:**
- Show departments as small purple badges on course cards
- Show "No department" if none selected
- Added year display

#### `course_full_summary.html`
**Changed:**
- Display departments in header
- Updated for visual consistency

---

### 6. Data Seeding

Created management command: `scan/management/commands/seed_departments.py`

**Usage:**
```bash
python manage.py seed_departments
```

**Seeded Departments:**
- Health Science
- Criminal Justice
- Education
- Business
- Agriculture

---

## API Design Philosophy

### Open API (No Authentication)
- All endpoints are public
- Designed for mobile app consumption
- No rate limiting (for now)

### Response Format
- All timestamps as Unix timestamps (integers)
- Departments returned as array of objects
- Efficient queries with `prefetch_related()`

### Caching Strategy
- Metadata is small and cached forever on client
- Full text only fetched when needed
- Supports offline-first mobile app

---

## Database Schema

```
Department (scan_department)
├── id (PK)
├── name (unique)
├── created_at
└── updated_at

Course (scan_course)
├── id (PK)
├── name
├── year
├── description
├── created_at
└── updated_at

Course_Departments (scan_course_departments)
├── id (PK)
├── course_id (FK → Course)
└── department_id (FK → Department)

Topic (scan_topic)
├── id (PK)
├── course_id (FK → Course)
├── title
├── raw_text
├── refined_summary
├── page_range
├── order
├── created_at
└── updated_at
```

---

## Testing Checklist

- [x] Create course with multiple departments
- [x] Display departments on course cards
- [x] API returns correct department data
- [x] Full summary includes departments
- [x] Backward compatibility (old courses work)
- [x] No duplicate departments created
- [x] Efficient database queries (no N+1)

---

## Files Changed

**Modified:**
- `scan/models.py`
- `scan/views.py`
- `scan/urls.py`
- `scan/templates/scan/partials/create_course.html`
- `scan/templates/scan/partials/course_detail.html`
- `scan/templates/scan/partials/library.html`
- `scan/templates/scan/partials/course_full_summary.html`

**Created:**
- `scan/management/commands/seed_departments.py`
- New migrations (auto-generated)

**Unchanged:**
- `scan/templates/scan/partials/home.html`
- `scan/templates/scan/partials/scan.html`
- `scan/templates/scan/partials/save_form.html`
- `scan/templates/scan/partials/topic_detail.html`
- `scan/templates/scan/partials/edit_refined.html`
- `scan/utils/ocr.py`
- `settings.py`

---

## Key Takeaways

1. **Reusable over repetitive** - DRY principle maintained
2. **Purpose-driven changes** - Only modified what was necessary
3. **Backward compatible** - Old functionality preserved
4. **Performance optimized** - Used `prefetch_related()` to avoid N+1 queries
5. **Type-safe API** - Clear response formats for mobile consumption