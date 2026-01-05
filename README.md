# Study Companion Backend - Django API & Premium Management

A Django-powered backend for OCR text extraction, AI-powered study note refinement with dynamic difficulty levels, premium user management, and RESTful API for mobile/web clients.

---

## 📚 Overview

Study Companion Backend provides:
1. **OCR Processing** - Extracts text from images via Google Cloud Vision (Colab GPU)
2. **AI Refinement** - Transforms messy OCR into structured Q&A using Gemini & Groq
3. **Dynamic Difficulty** - Easy, Medium, Difficult levels for personalized learning (NEW)
4. **Direct Text Input** - Bypass OCR, paste text from Word/PDF directly
5. **Premium System** - Name+code authentication with topic access control
6. **REST API** - Serves filtered data to React PWA frontend
7. **Department System** - Organizes courses by academic departments
8. **Admin Panel** - Manage courses, topics, departments, and premium users

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
│  │  Text Input  │  Q&A Format  │   Difficulty    │ │
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
│   │   ├── Topic              # Study topics with difficulty_level (NEW)
│   │   └── AIRefine           # AI-generated refinements with difficulty
│   │
│   ├── views.py               # Web views + API endpoints
│   ├── ai_views.py            # AI refine endpoints (UPDATED)
│   ├── urls.py                # App URL routing
│   │
│   ├── utils/
│   │   ├── ocr.py             # OCR integration
│   │   └── ai.py              # Gemini/Groq with difficulty prompts (UPDATED)
│   │
│   ├── templates/             # HTML templates
│   │   └── scan/partials/
│   │       ├── home.html
│   │       ├── library.html
│   │       ├── ai_refine.html         # Difficulty selector (UPDATED)
│   │       ├── text_input.html        # No difficulty field (UPDATED)
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
│   ├── PHASE3.md              # Study mode Q&A format
│   └── PHASE4.md              # Dynamic difficulty system (NEW)
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
- difficulty_level ('easy'/'medium'/'difficult', default='medium') ← NEW
- premium_users (ManyToMany → PremiumUser)
- created_at (auto)
- updated_at (auto)

Example: "Cell Structure - Pages 1-5" (Medium difficulty)
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
- difficulty_level ('easy'/'medium'/'difficult') ← NEW
- created_at (auto)
- updated_at (auto)

Unique: (topic, provider, difficulty_level) ← UPDATED
```

---

## 🎯 Difficulty System (Phase 4)

### Three Learning Levels

**⚡ Easy - Quick Recognition**
- **Purpose**: Fast review, habit building
- **Content**: Basic facts, simple language
- **Best for**: Daily reviews, memorization, cramming
- **Example**: "Answer: Infected mosquito bite"

**📚 Medium - Understanding**
- **Purpose**: Conceptual understanding
- **Content**: WHY/HOW explanations, local context
- **Best for**: Regular study, learning new material
- **Example**: "Answer: Infected female Anopheles mosquito bite"

**🎓 Difficult - Mastery**
- **Purpose**: Deep learning, exam excellence
- **Content**: Cause-and-effect, technical terms, scenarios
- **Best for**: Exam prep, thesis work, teaching
- **Example**: "Answer: Plasmodium parasite via infected Anopheles bite"

### User Workflow

```
1. Create topic (no difficulty selection)
2. Navigate to AI Refine page
3. Select difficulty: Easy | Medium | Difficult
4. Generate with Gemini/Groq
5. AI creates content at selected level
6. Can regenerate at different difficulty anytime
```

### Frontend Display

Topics show difficulty badge:
- ⚡ Easy
- 📚 Medium  
- 🎓 Difficult

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
```

---

### Public API (Filtered by User)

#### Topics (Access Controlled)

**Get full topic**
```http
GET /api/topics/<topic_id>/?user_id=2
```
Success (200):
```json
{
  "id": 5,
  "title": "Advanced Genetics",
  "difficulty_level": "medium",
  "refined_summary": "Q1: What is genetics?\nAnswer: Study of genes and heredity\n\nExplanation: How traits pass from parents to children\n\nExample: Eye color inherited from parents\n\n---",
  "raw_text": "genetics is...",
  "course_name": "BIO 202",
  "departments": ["Health Science"],
  "is_premium": true,
  "updated_at": 1703002000
}
```

---

#### AI Refine

**Generate AI refine with difficulty**
```http
POST /topics/<topic_id>/generate-ai/
Content-Type: application/x-www-form-urlencoded

provider=gemini  # or 'groq' or 'both'
difficulty=medium  # or 'easy' or 'difficult' (NEW)
```

Response:
```json
{
  "gemini": {
    "success": true,
    "qa_count": 5,
    "processing_time": 7.2,
    "difficulty": "medium",
    "preview": "Q1: What is..."
  }
}
```

---

## 🤖 AI Integration

### Difficulty-Specific Prompts

**Easy Level**:
```
- Answer: Simple, direct facts (4-6 words)
- Explanation: Basic "what" - no mechanisms (6-8 words)
- Example: Straightforward scenario (5-7 words)
```

**Medium Level**:
```
- Answer: Key concept (4-6 words)
- Explanation: WHY/HOW it works (6-8 words)
- Example: Specific local context (5-7 words)
```

**Difficult Level**:
```
- Answer: Precise definition with technical terms (4-6 words)
- Explanation: Cause-and-effect mechanisms (6-8 words)
- Example: Real-world Liberian scenario (5-7 words)
```

### AI Providers

**Gemini (Google)**
- Model: `gemini-2.5-flash`
- Speed: 5-10 seconds
- Quality: Detailed, comprehensive

**Groq (Llama 3)**
- Model: Auto-detected (llama-3.3 > 3.1 > 3.0)
- Speed: 2-5 seconds (faster)
- Quality: Concise, practical

---

## 📝 Direct Text Input

### Text Input Page

**URL:** `/text-input/`

**Features:**
- Bypass OCR completely
- Paste text from Word, PDF, websites
- Select existing course or create new
- Set topic title and page range
- Choose community or premium type
- **No difficulty selection** (set when generating AI)

---

## 🧪 Testing

### Difficulty System Tests
- [ ] Generate Easy difficulty
- [ ] Generate Medium difficulty
- [ ] Generate Difficult difficulty
- [ ] Regenerate same topic at different difficulty
- [ ] Compare Easy vs Medium vs Difficult outputs
- [ ] Verify difficulty saved to database
- [ ] Check AI prompt uses correct difficulty

### Premium User Tests
- [ ] Create premium user
- [ ] Login existing user
- [ ] Assign topics to user
- [ ] Filter topics by user
- [ ] Access control for premium topics

### API Tests
- [ ] GET /api/topics/5/?user_id=2 (check difficulty_level in response)
- [ ] POST /topics/5/generate-ai/ with difficulty=easy
- [ ] POST /topics/5/generate-ai/ with difficulty=difficult

---

## 📖 Documentation

- **[PHASE1.md](docs/PHASE1.md)** - AI & Department migration, text input
- **[PHASE2.md](docs/PHASE2.md)** - Premium user system
- **[PHASE3.md](docs/PHASE3.md)** - Study mode Q&A format
- **[PHASE4.md](docs/PHASE4.md)** - Dynamic difficulty system (NEW)

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

### Phase 3 ✅ (Completed)
- [x] Q&A format standardization
- [x] Table answer support
- [x] Progressive disclosure structure
- [x] Chunking-ready output format
- [x] Frontend parsing compatibility

### Phase 4 ✅ (Current - NEW)
- [x] Dynamic difficulty system (Easy/Medium/Difficult)
- [x] User-controlled difficulty selection
- [x] Difficulty-specific AI prompts
- [x] Topic.difficulty_level field
- [x] AIRefine.difficulty_level field
- [x] Regeneration at different difficulties
- [x] Real-time UI difficulty indicator
- [x] Removed difficulty from topic creation

### Phase 5 🚧 (Planned)
- [ ] User authentication (Django users)
- [ ] Study progress tracking
- [ ] Bulk AI generation
- [ ] PDF export with Q&A format
- [ ] Usage analytics
- [ ] Rate limiting
- [ ] Caching layer

---

## 👨‍💻 Support

- **Documentation**: docs/PHASE1.md through docs/PHASE4.md
- **Issues**: GitHub Issues
- **Email**: studycompanion@gmail.com

---

**Built with ❤️ for Liberian students at community colleges.**