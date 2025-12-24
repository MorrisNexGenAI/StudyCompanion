

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