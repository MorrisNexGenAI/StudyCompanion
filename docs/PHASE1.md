# Phase 1: Django Backend Migration & AI Integration

## Overview
Phase 1 involved two major migrations:
1. **Department System**: Migrated from single `subject` CharField to many-to-many `departments` relationship
2. **AI Refine System**: Added AI-powered text refinement using Gemini and Groq APIs

---

## Part A: Department System Migration

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

#### New Model: AIRefine
```python
class AIRefine(BaseModel):
    """Stores AI-generated refined summaries"""
    
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('groq', 'Groq Llama'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='ai_refines')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    refined_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)
    qa_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['topic', 'provider']
```

---

### 2. Database Migrations

#### Created Tables:
- `scan_department` - Stores department names
- `scan_course_departments` - Many-to-many relationship table
- `scan_airefine` - Stores AI-generated refinements

#### Migration Commands:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_departments
```

---

### 3. API Endpoints (`scan/views.py`)

#### Department & Course APIs

**List Departments**
```python
GET /api/departments/
Response: [{"id": 1, "name": "Health Science"}, ...]
```

**Courses by Department**
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

**Topics by Course (Metadata)**
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

**Full Topic with Content**
```python
GET /api/topics/<topic_id>/
Response: {
    "id": 1,
    "title": "Cell Division",
    "refined_summary": "...",
    "raw_text": "...",
    "course_name": "BIO 202",
    "departments": ["Health Science"],
    "updated_at": 1703001234
}
```

---

### 4. AI Refine System (`scan/ai_views.py`)

#### New AI Views

**AI Refine Comparison Page**
```python
GET /topics/<topic_id>/ai-refine/
Shows: Raw OCR | Manual Refine | AI Refines (Gemini + Groq)
```

**Generate AI Refine**
```python
POST /topics/<topic_id>/generate-ai/
Body: provider=gemini|groq|both
Response: {
    "gemini": {"success": true, "qa_count": 15, "processing_time": 8.2},
    "groq": {"success": true, "qa_count": 12, "processing_time": 3.5}
}
```

**Select AI Refine**
```python
POST /topics/<topic_id>/select-ai/
Body: selection=gemini|groq|manual
Action: Saves selected refine to topic.refined_summary
```

**AI Status Check**
```python
GET /ai-status/
Response: {
    "gemini": {"ok": true, "message": "Gemini connection successful"},
    "groq": {"ok": true, "message": "Groq connection successful (using llama-3.3-70b-versatile)"}
}
```

---

### 5. AI Utilities (`scan/utils/ai.py`)

#### Key Features

**Gemini Integration**
- Model: `gemini-2.5-flash`
- Max tokens: 8000
- Temperature: 0.7
- Retry logic with exponential backoff
- Rate limit handling (429 errors)

**Groq Integration**
- Auto-detects best available model (3.3 > 3.1 > 3.0)
- Max tokens: 6000
- Temperature: 0.7
- Faster processing than Gemini

**Smart Formatting**
- Removes markdown symbols (###, **)
- Adds proper spacing between sections
- Ensures brief, concise answers (1-2 sentences)
- Full tables/lists preserved
- Localized examples for Liberia/West Africa

**Example Output Format**
```
Q1: What causes bacterial diseases?
Answer: Pathogenic bacteria reproduce in the body and release toxins.

Explanation: Understanding causative agents helps in prevention.

Example: Cholera outbreaks in Monrovia occur when Vibrio cholerae contaminates water during flooding.

---
```

---

### 6. Templates

#### New Templates
- `scan/partials/ai_refine.html` - Comparison page with 3 columns
- `scan/partials/ai_select_success.html` - Success confirmation page

#### Updated Templates
- `edit_refined.html` - Added "Try AI Refine" banner
- `topic_detail.html` - Added "🤖 AI Refine" button

#### Key UI Features
- Selective generation (Gemini only, Groq only, or Both)
- Regenerate buttons for each AI
- Real-time status updates
- Preview of generated Q&As
- Side-by-side comparison

---

### 7. Configuration (`settings.py`)

#### New Environment Variables
```python
# AI API Keys
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# CORS for PWA
CORS_ALLOWED_ORIGINS = [...]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [...]
```

#### Database Configuration
```python
# PostgreSQL (Production) or SQLite (Development)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {'default': dj_database_url.config(...)}
else:
    DATABASES = {'default': {'ENGINE': 'sqlite3', ...}}
```

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
├── departments (M2M → Department)
├── created_at
└── updated_at

Topic (scan_topic)
├── id (PK)
├── course (FK → Course)
├── title
├── raw_text (OCR output)
├── refined_summary (manual or AI)
├── page_range
├── order
├── created_at
└── updated_at

AIRefine (scan_airefine)
├── id (PK)
├── topic (FK → Topic)
├── provider (gemini/groq)
├── refined_text
├── status (pending/processing/completed/failed)
├── error_message
├── processing_time
├── qa_count
├── created_at
└── updated_at
```

---

## AI Prompt Engineering

### Localization Context
All AI prompts include:
- **Location**: Liberia, West Africa
- **Health examples**: Malaria, cholera, Ebola, typhoid
- **Business examples**: Waterside Market, Red Light Market, street vendors
- **Criminal justice**: Liberian courts, police
- **Agriculture**: Cassava, rubber, rice farming

### Format Requirements
- Brief answers (1-2 sentences)
- Brief explanations (1-2 sentences)
- Brief examples (1-2 sentences)
- Exception: Full tables/lists preserved
- Blank lines between sections
- No markdown symbols in output

---

## Testing Checklist

**Department System**
- [x] Create course with multiple departments
- [x] Display departments on course cards
- [x] API returns correct department data
- [x] Full summary includes departments
- [x] No duplicate departments created

**AI Refine System**
- [x] Generate with Gemini only
- [x] Generate with Groq only
- [x] Generate with both simultaneously
- [x] Regenerate individual AI
- [x] Select and save AI refine
- [x] Handle API failures gracefully
- [x] Rate limit retry logic works
- [x] Formatting is clean (no ### or **)
- [x] Examples are localized
- [x] Tables preserved correctly

---

## Files Changed

**Modified:**
- `scan/models.py` - Added Department, AIRefine models
- `scan/views.py` - Updated for departments
- `scan/urls.py` - Added AI routes
- `settings.py` - Added AI keys, CORS config

**Created:**
- `scan/ai_views.py` - AI refine views
- `scan/utils/ai.py` - AI integration logic
- `scan/templates/scan/partials/ai_refine.html`
- `scan/templates/scan/partials/ai_select_success.html`
- `scan/management/commands/seed_departments.py`

**Updated Templates:**
- `create_course.html` - Multi-select departments
- `course_detail.html` - Display department badges
- `edit_refined.html` - AI refine option
- `topic_detail.html` - AI refine button
- `library.html` - Department display
- `course_full_summary.html` - Department in header

---

## Environment Setup

### Required API Keys (Free)

**Google Gemini**
```bash
# Get key from: https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="your_gemini_key_here"
```

**Groq**
```bash
# Get key from: https://console.groq.com/keys
export GROQ_API_KEY="your_groq_key_here"
```

### Production Variables
```bash
# Database
DATABASE_URL="postgresql://..."

# Security
DJANGO_SECRET_KEY="..."
DEBUG="False"
ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# CORS
CORS_ALLOWED_ORIGINS="https://pwa.yourdomain.com"
CSRF_TRUSTED_ORIGINS="https://yourdomain.com,https://pwa.yourdomain.com"

# OCR
COLAB_OCR_URL="https://your-ngrok-url.ngrok-free.dev"
```

---

## Performance Optimizations

1. **Database Queries**
   - `prefetch_related('departments')` on course queries
   - Avoids N+1 query problem

2. **AI Processing**
   - Async-ready (can process both AIs simultaneously)
   - Exponential backoff for rate limits
   - Caches results in database

3. **Static Files**
   - WhiteNoise for production serving
   - Compressed manifest storage

---

## Key Achievements

1. ✅ **Multi-department support** - Courses can belong to multiple departments
2. ✅ **AI-powered refinement** - Gemini and Groq integration
3. ✅ **Localized content** - Examples relevant to Liberia
4. ✅ **Clean formatting** - No markdown symbols in output
5. ✅ **Selective generation** - Generate with one or both AIs
6. ✅ **Robust error handling** - Rate limits, failures gracefully handled
7. ✅ **Brief & concise** - 1-2 sentence answers/explanations/examples
8. ✅ **Table preservation** - Important data structures maintained
9. ✅ **Mobile-ready API** - All endpoints support PWA consumption

---

## Next Steps (Phase 2)

- [ ] User authentication
- [ ] Bulk AI generation (entire course at once)
- [ ] Export refined summaries to PDF
- [ ] AI prompt customization per department
- [ ] Usage analytics dashboard
- [ ] Rate limiting for API endpoints