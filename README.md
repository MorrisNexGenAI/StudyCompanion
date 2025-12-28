# Study Companion Backend - Django API & Premium Management

A Django-powered backend for OCR text extraction, AI-powered study note refinement, premium user management, and RESTful API for mobile/web clients.

---

## 📚 Overview

Study Companion Backend provides:
1. **OCR Processing** - Extracts text from images via Google Cloud Vision (Colab GPU)
2. **AI Refinement** - Transforms messy OCR into structured Q&A using Gemini & Groq
3. **Direct Text Input** - Bypass OCR, paste text from Word/PDF directly (NEW)
4. **Premium System** - Name+code authentication with topic access control
5. **REST API** - Serves filtered data to React PWA frontend
6. **Department System** - Organizes courses by academic departments
7. **Admin Panel** - Manage courses, topics, departments, and premium users

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Client Layer                        │
│  (React PWA, Mobile App, Admin Panel)               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Django REST API                         │
│  ┌──────────────┬──────────────┬─────────────────┐ │
│  │ Departments  │    Topics    │   AI Refine     │ │
│  │   Courses    │  Raw/Refined │  Gemini/Groq    │ │
│  │  Premium     │  Filtering   │   Access Ctrl   │ │
│  │  Text Input  │  Q&A Format  │   Context-Aware │ │
│  └──────────────┴──────────────┴─────────────────┘ │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            External Services                         │
│  ┌──────────┬──────────────┬──────────────────────┐│
│  │   OCR    │  Gemini AI   │      Groq AI         ││
│  │  (Colab) │  (Google)    │     (Llama 3)        ││
│  └──────────┴──────────────┴──────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or pipenv
- PostgreSQL (production) or SQLite (development)
- Google Gemini API key (free)
- Groq API key (free)

---

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd cafphy-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed departments
python manage.py seed_departments

# 7. Create superuser (optional)
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

**Backend runs on:** `http://localhost:8000`

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Django Core
DJANGO_SECRET_KEY="your-secret-key-here"
DEBUG="True"  # Set to False in production
ALLOWED_HOSTS="localhost,127.0.0.1,.yourdomain.com"

# Database (Development - SQLite)
# Leave empty to use SQLite automatically

# Database (Production - PostgreSQL)
DATABASE_URL="postgresql://user:password@host:5432/dbname"

# AI API Keys (Get for free)
GEMINI_API_KEY="your_gemini_key"  # https://aistudio.google.com/app/apikey
GROQ_API_KEY="your_groq_key"      # https://console.groq.com/keys

# OCR Service
COLAB_OCR_URL="https://your-ngrok-url.ngrok-free.dev"

# CORS (for React PWA)
CORS_ALLOWED_ORIGINS="http://localhost:3000,https://your-pwa.vercel.app"
CSRF_TRUSTED_ORIGINS="http://localhost:8000,https://your-backend.com"
```

---

## 📁 Project Structure

```
cafphy-backend/
├── scanner/                    # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # Root URL routing
│   └── wsgi.py                # WSGI entry point
│
├── scan/                      # Main application
│   ├── models.py              # Database models
│   │   ├── Department         # Academic departments
│   │   ├── Course             # Courses (many-to-many with departments)
│   │   ├── Topic              # Study topics with OCR text
│   │   └── AIRefine           # AI-generated refinements
│   │
│   ├── views.py               # Web views + API endpoints
│   ├── ai_views.py            # AI refine endpoints
│   ├── urls.py                # App URL routing
│   │
│   ├── utils/
│   │   ├── ocr.py             # OCR integration
│   │   └── ai.py              # Gemini/Groq integration (UPDATED)
│   │
│   ├── templates/             # HTML templates
│   │   └── scan/partials/
│   │       ├── home.html
│   │       ├── library.html
│   │       ├── ai_refine.html
│   │       ├── text_input.html    # NEW: Direct text input
│   │       └── ...
│   │
│   └── management/commands/
│       └── seed_departments.py
│
├── premium_users/             # Premium user app
│   ├── models.py              # PremiumUser model
│   ├── views.py               # Premium user management + API
│   ├── urls.py                # Premium routes
│   └── templates/             # Premium user templates
│       └── premium_users/
│           ├── manage_users.html
│           └── send_topics.html
│
├── core/                      # Base app
│   └── models.py              # BaseModel (timestamps)
│
├── static/                    # Static files (CSS, JS)
├── media/                     # Uploaded files
├── db.sqlite3                 # SQLite database (dev)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── docs/                      # Documentation
│   ├── PHASE1.md              # AI & Department migration
│   ├── PHASE2.md              # Premium system
│   └── PHASE3.md              # Study mode Q&A format (NEW)
└── README.md                  # This file
```

---

## 🗄️ Database Models

### Department
```python
- id (Primary Key)
- name (unique, max 200 chars)
- created_at (auto)
- updated_at (auto)

Example: "Health Science", "Criminal Justice", "Business"
```

### Course
```python
- id (Primary Key)
- name (max 200 chars)
- year (max 20 chars, e.g., "2024")
- description (text)
- departments (ManyToMany → Department)
- is_deleted (soft delete flag)
- created_at (auto)
- updated_at (auto)

Example: "BIO 202", departments=["Health Science"]
```

### Topic
```python
- id (Primary Key)
- course (ForeignKey → Course)
- title (max 300 chars)
- raw_text (OCR output or direct input, text)
- refined_summary (manual or AI, text)
- page_range (e.g., "Pages 1-5")
- order (integer for sorting)
- is_premium (boolean)
- is_deleted (soft delete flag)
- premium_users (ManyToMany → PremiumUser)
- created_at (auto)
- updated_at (auto)

Example: "Cell Structure - Pages 1-5"
```

### PremiumUser
```python
- id (Primary Key)
- name (max 100 chars)
- code (4 alphanumeric chars, unique)
- is_active (boolean, default True)
- created_at (auto)
- updated_at (auto)

Unique together: (name, code)

Example: name="Emmanuel Cooper", code="EC21"
```

### AIRefine
```python
- id (Primary Key)
- topic (ForeignKey → Topic)
- provider ('gemini' or 'groq')
- refined_text (AI output, text)
- status ('pending'/'processing'/'completed'/'failed')
- error_message (text)
- processing_time (float, seconds)
- qa_count (integer)
- created_at (auto)
- updated_at (auto)

Unique: (topic, provider)
```

---

## 🔌 API Endpoints

### Premium Authentication

**Register or Login**
```http
POST /premium/api/register-or-login/
Content-Type: application/json

Body:
{
  "name": "Emmanuel Cooper",
  "code": "EC21"
}

Success Response (201):
{
  "user_id": 2,
  "name": "Emmanuel Cooper",
  "code": "EC21",
  "is_new": true
}

Error Response (400/403):
{
  "error": "This code is already linked to another user"
}
```

---

### Public API (Filtered by User)

#### Departments

**List all departments**
```http
GET /api/departments/
```
Response:
```json
[
  {"id": 1, "name": "Health Science"},
  {"id": 2, "name": "Criminal Justice"}
]
```

**Get courses in department**
```http
GET /api/departments/<dept_id>/courses/?user_id=2
```
Response:
```json
[
  {
    "id": 1,
    "name": "BIO 202",
    "year": "2024",
    "departments": [{"id": 1, "name": "Health Science"}],
    "topic_count": 5,
    "refined_count": 3
  }
]
```

---

#### Topics (Access Controlled)

**Get topics in course**
```http
GET /api/courses/<course_id>/topics/?user_id=2
```
Response:
```json
[
  {
    "id": 1,
    "title": "Cell Structure",
    "page_range": "Pages 1-5",
    "is_premium": false,
    "is_refined": true,
    "updated_at": 1703001234
  },
  {
    "id": 5,
    "title": "Advanced Genetics",
    "page_range": "Pages 10-15",
    "is_premium": true,
    "is_refined": true,
    "updated_at": 1703002000
  }
]
```

**Get full topic**
```http
GET /api/topics/<topic_id>/?user_id=2
```
Success (200):
```json
{
  "id": 5,
  "title": "Advanced Genetics",
  "refined_summary": "Q1: What is genetics?\nAnswer: Study of genes and heredity\n\nExplanation: How traits pass from parents to children\n\nExample: Eye color inherited from parents\n\n---\n\nQ2: What are chromosomes?\nAnswer: DNA structures carrying genetic information\n...",
  "raw_text": "genetics is...",
  "course_name": "BIO 202",
  "departments": ["Health Science"],
  "is_premium": true,
  "updated_at": 1703002000
}
```

Access Denied (403):
```json
{
  "error": "Access denied. This is a premium topic.",
  "is_premium": true,
  "requires_login": true
}
```

---

#### AI Refine

**Generate AI refine**
```http
POST /topics/<topic_id>/generate-ai/
Content-Type: application/x-www-form-urlencoded

provider=gemini  # or 'groq' or 'both'
```

**Select AI refine**
```http
POST /topics/<topic_id>/select-ai/
Content-Type: application/x-www-form-urlencoded

selection=gemini  # or 'groq' or 'manual'
```

**Check AI status**
```http
GET /ai-status/
```

---

## 🔐 Premium User Management

### Admin Interface

**Manage Premium Users**
- URL: `/premium/manage/`
- Create, edit, activate/deactivate users
- Search by name or code
- Filter by active/inactive

**Send Premium Topics**
- URL: `/premium/send-topics/`
- Assign premium topics to specific users
- Bulk select users
- See who has access to what

**Manage Premium Topics**
- URL: `/manage-premium-topics/`
- View all premium topics
- Edit assignments
- Soft delete topics

---

### Access Control Logic

**Topic Filtering:**
```python
def filter_topics_for_user(topics_queryset, user_id=None):
    if not user_id:
        # No user_id = only community topics
        return topics_queryset.filter(is_premium=False, is_deleted=False)
    
    try:
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        
        # Return:
        # 1. All community topics, OR
        # 2. Premium topics where user is explicitly assigned
        return topics_queryset.filter(
            Q(is_premium=False) | Q(is_premium=True, premium_users=user),
            is_deleted=False
        ).distinct()
    except PremiumUser.DoesNotExist:
        return topics_queryset.filter(is_premium=False, is_deleted=False)
```

**Topic Access Check:**
```python
def check_topic_access(topic, user_id=None):
    # Community topics = always accessible
    if not topic.is_premium:
        return True
    
    # Premium topics require explicit assignment
    if not user_id:
        return False
    
    try:
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        return topic.is_accessible_by(user)
    except PremiumUser.DoesNotExist:
        return False
```

---

## 🤖 AI Integration (Phase 1 - Enhanced)

### Gemini (Google)

**Model:** `gemini-2.5-flash`
- Speed: 5-10 seconds
- Quality: Detailed, comprehensive
- Token Limit: 8000 output tokens

### Groq (Llama 3)

**Model:** Auto-detected (llama-3.3 > 3.1 > 3.0)
- Speed: 2-5 seconds (faster)
- Quality: Concise, practical
- Token Limit: 6000 output tokens

### Enhanced Prompt (Phase 1 Update)

**Strict Word Count Enforcement:**
- Answer: 4-6 words MAXIMUM
- Explanation: 6-8 words MAXIMUM
- Example: 5-7 words MAXIMUM

**Formatting Rules:**
- No markdown symbols (###, **)
- Clean separation between sections
- Proper blank lines
- Exception for tables/lists (no Explanation/Example)

**Content Quality:**
- One sentence per field
- No comma chains
- No repeating questions
- Concrete examples only
- Context-aware for Liberia/West Africa

### Localization

All AI examples are contextualized for **Liberia, West Africa**:
- Health: Malaria, cholera, Ebola, typhoid
- Business: Waterside Market, Red Light Market
- Criminal Justice: Liberian courts, police
- Agriculture: Cassava, rubber, rice farming
- Education: University of Liberia, WASSCE exams

---

## 📝 Direct Text Input (Phase 1 Feature)

### Text Input Page

**URL:** `/text-input/`

**Features:**
- Bypass OCR completely
- Paste text from Word, PDF, websites
- Select existing course or create new
- Set topic title and page range
- Choose community or premium type
- Instant topic creation

**Use Cases:**
- Text already extracted from PDF
- Content from Word documents
- Web articles/content
- Manual typing
- Faster than OCR processing

**Process Flow:**
```
1. Admin visits /text-input/
2. Selects course (existing or new)
3. Enters topic title
4. Pastes text content
5. Chooses topic type (community/premium)
6. Submits form
7. Topic created instantly
8. Redirected to topic detail
```

---

## 📦 Dependencies

```txt
# Core
Django==5.1
django-cors-headers==4.3.1
whitenoise==6.5.0

# Database
dj-database-url==2.1.0
psycopg2-binary==2.9.9

# Environment
python-dotenv==1.0.0

# Image Processing
Pillow==10.0.0

# HTTP Requests
requests==2.31.0
```

---

## 🧪 Testing

### Premium User Tests
- [ ] Create premium user
- [ ] Login existing user
- [ ] Invalid code format error
- [ ] Duplicate code error
- [ ] Assign topics to user
- [ ] Filter topics by user
- [ ] Access denied for non-assigned topic
- [ ] Community topics always visible

### API Tests
- [ ] GET /api/departments/
- [ ] GET /api/departments/1/courses/?user_id=2
- [ ] GET /api/courses/1/topics/?user_id=2
- [ ] GET /api/topics/5/?user_id=2 (assigned)
- [ ] GET /api/topics/5/?user_id=3 (not assigned = 403)
- [ ] POST /premium/api/register-or-login/

### Text Input Tests
- [ ] Create topic from pasted text
- [ ] Select existing course
- [ ] Create new course
- [ ] Set community topic
- [ ] Set premium topic
- [ ] Validation errors

### AI Refine Tests
- [ ] Generate Gemini refine
- [ ] Generate Groq refine
- [ ] Word count compliance
- [ ] Table handling
- [ ] Formatting cleanup
- [ ] Local context in examples

---

## 🚢 Deployment

### Render (Recommended)

1. **Create PostgreSQL database**
2. **Create Web Service**
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn scanner.wsgi:application`

3. **Environment Variables**
   ```
   DJANGO_SECRET_KEY=<generate-random-key>
   DEBUG=False
   DATABASE_URL=<from-postgresql>
   GEMINI_API_KEY=<your-key>
   GROQ_API_KEY=<your-key>
   CORS_ALLOWED_ORIGINS=https://your-pwa.vercel.app
   ```

4. **Deploy** - Automatic on git push

---

## 🔒 Security

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure CORS properly
- [ ] Add CSRF_TRUSTED_ORIGINS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HSTS headers
- [ ] Add rate limiting

---

## 📖 Documentation

- **[PHASE1.md](docs/PHASE1.md)** - AI & Department migration, text input
- **[PHASE2.md](docs/PHASE2.md)** - Premium user system
- **[PHASE3.md](docs/PHASE3.md)** - Study mode Q&A format (NEW)
- **Django Docs** - https://docs.djangoproject.com/
- **Gemini API** - https://ai.google.dev/docs
- **Groq API** - https://console.groq.com/docs

---

## 🎯 Version History

### Phase 1 ✅ (Completed)
- [x] Department system
- [x] AI refine (Gemini + Groq)
- [x] Enhanced prompts with strict word limits
- [x] Direct text input feature
- [x] Formatting cleanup
- [x] REST API
- [x] Localized examples

### Phase 2 ✅ (Completed)
- [x] Premium user model
- [x] Name + code authentication
- [x] Topic access control
- [x] Admin user management
- [x] Topic assignment system
- [x] Soft delete functionality

### Phase 3 ✅ (Current)
- [x] Q&A format standardization
- [x] Table answer support
- [x] Progressive disclosure structure
- [x] Chunking-ready output format
- [x] Frontend parsing compatibility

### Phase 4 🚧 (Planned)
- [ ] User authentication (Django users)
- [ ] Bulk AI generation
- [ ] PDF export with Q&A format
- [ ] Usage analytics
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Study progress API endpoints

---

## 👨‍💻 Support

- **Documentation**: docs/PHASE1.md, docs/PHASE2.md, docs/PHASE3.md
- **Issues**: GitHub Issues
- **Email**: support@cafphy.com

---

**Built with ❤️ for Liberian students at community colleges.**