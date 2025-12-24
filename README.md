# Study Companion Backend - Django API & AI Integration

A Django-powered backend for OCR text extraction, AI-powered study note refinement, and RESTful API for mobile/web clients.

---

## 📚 Overview

Study Companion Backend provides:
1. **OCR Processing** - Extracts text from images via Google Cloud Vision (Colab GPU)
2. **AI Refinement** - Transforms messy OCR into structured Q&A using Gemini & Groq
3. **REST API** - Serves data to React PWA frontend
4. **Department System** - Organizes courses by academic departments
5. **Admin Panel** - Manage courses, topics, and departments

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
│   │   └── ai.py              # Gemini/Groq integration
│   │
│   ├── templates/             # HTML templates
│   │   └── scan/partials/
│   │       ├── home.html
│   │       ├── library.html
│   │       ├── ai_refine.html
│   │       └── ...
│   │
│   └── management/commands/
│       └── seed_departments.py
│
├── core/                      # Base app
│   └── models.py              # BaseModel (timestamps)
│
├── static/                    # Static files (CSS, JS)
├── media/                     # Uploaded files
├── db.sqlite3                 # SQLite database (dev)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── PHASE1.md                  # Migration documentation
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
- created_at (auto)
- updated_at (auto)

Example: "BIO 202", departments=["Health Science"]
```

### Topic
```python
- id (Primary Key)
- course (ForeignKey → Course)
- title (max 300 chars)
- raw_text (OCR output, text)
- refined_summary (manual or AI, text)
- page_range (e.g., "Pages 1-5")
- order (integer for sorting)
- created_at (auto)
- updated_at (auto)

Example: "Cell Structure - Pages 1-5"
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

Unique: (topic, provider) - one AI refine per provider per topic
```

---

## 🔌 API Endpoints

### Public API (No Authentication Required)

#### Departments

**List all departments**
```http
GET /api/departments/
```
Response:
```json
[
  {"id": 1, "name": "Health Science"},
  {"id": 2, "name": "Criminal Justice"},
  {"id": 3, "name": "Business"}
]
```

**Get courses in department**
```http
GET /api/departments/<dept_id>/courses/
```
Response:
```json
[
  {
    "id": 1,
    "name": "BIO 202",
    "year": "2024",
    "departments": [{"id": 1, "name": "Health Science"}],
    "topic_count": 10,
    "refined_count": 8
  }
]
```

---

#### Courses & Topics

**Get topics in course (metadata only)**
```http
GET /api/courses/<course_id>/topics/
```
Response:
```json
[
  {
    "id": 1,
    "title": "Cell Structure",
    "page_range": "Pages 1-5",
    "updated_at": 1703001234,
    "is_refined": true
  }
]
```

**Get full topic with content**
```http
GET /api/topics/<topic_id>/
```
Response:
```json
{
  "id": 1,
  "title": "Cell Structure",
  "page_range": "Pages 1-5",
  "refined_summary": "Q1: What is a cell?\nAnswer: ...",
  "raw_text": "--- Page 1 ---\ncel structur...",
  "course_name": "BIO 202",
  "course_year": "2024",
  "departments": ["Health Science"],
  "updated_at": 1703001234,
  "created_at": 1702995000
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
Response:
```json
{
  "gemini": {
    "success": true,
    "qa_count": 15,
    "processing_time": 8.2,
    "preview": "Q1: What is a cell?\nAnswer: ..."
  },
  "groq": {
    "success": true,
    "qa_count": 12,
    "processing_time": 3.5,
    "preview": "Q1: What is a cell?\nAnswer: ..."
  }
}
```

**Select AI refine**
```http
POST /topics/<topic_id>/select-ai/
Content-Type: application/x-www-form-urlencoded

selection=gemini  # or 'groq' or 'manual'
```
Saves selected refine to `topic.refined_summary`

**Check AI status**
```http
GET /ai-status/
```
Response:
```json
{
  "gemini": {
    "ok": true,
    "message": "Gemini connection successful"
  },
  "groq": {
    "ok": true,
    "message": "Groq connection successful (using llama-3.3-70b-versatile)"
  },
  "overall": true
}
```

---

## 🤖 AI Integration

### Gemini (Google)

**Model:** `gemini-2.5-flash`
- **Speed:** 5-10 seconds
- **Quality:** Detailed, comprehensive
- **Token Limit:** 8000 output tokens
- **Cost:** Free tier available
- **Best For:** Complex topics, detailed explanations

### Groq (Llama 3)

**Model:** Auto-detected (llama-3.3 > 3.1 > 3.0)
- **Speed:** 2-5 seconds (faster)
- **Quality:** Concise, practical
- **Token Limit:** 6000 output tokens
- **Cost:** Free tier available
- **Best For:** Quick summaries, simple topics

### AI Output Format

```
Q1: What causes malaria?
Answer: Malaria is caused by Plasmodium parasites transmitted by Anopheles mosquitoes.

Explanation: Understanding the cause helps in prevention and treatment strategies.

Example: In Monrovia, malaria cases spike during rainy season when mosquito breeding increases in standing water.

---

Q2: What are the symptoms of malaria?
Answer: Fever, chills, headache, nausea, and body aches are common symptoms.

Explanation: Early recognition of symptoms allows for timely treatment and prevents complications.

Example: At JFK Hospital, patients presenting with fever and chills are tested for malaria first.

---
```

### Localization

All AI examples are contextualized for **Liberia, West Africa**:
- **Health**: Malaria, cholera, Ebola, typhoid
- **Business**: Waterside Market, Red Light Market, street vendors
- **Criminal Justice**: Liberian courts, police
- **Agriculture**: Cassava, rubber, rice farming

---

## 📦 Dependencies

```txt
# Core
Django==5.1
django-cors-headers==4.3.1
whitenoise==6.5.0

# Database
dj-database-url==2.1.0
psycopg2-binary==2.9.9  # PostgreSQL

# Environment
python-dotenv==1.0.0

# Image Processing
Pillow==10.0.0

# HTTP Requests
requests==2.31.0

# AI Integration (built-in)
# Gemini API - requests library
# Groq API - requests library
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

### Manual Testing Checklist

**Department System**
- [ ] Create course with single department
- [ ] Create course with multiple departments
- [ ] View courses by department
- [ ] Display departments on course cards

**OCR & Topics**
- [ ] Upload images and extract text
- [ ] Save topic with raw OCR text
- [ ] View topic detail page
- [ ] Edit refined summary manually

**AI Refine**
- [ ] Generate with Gemini only
- [ ] Generate with Groq only
- [ ] Generate with both simultaneously
- [ ] Regenerate individual AI
- [ ] Compare AI outputs side-by-side
- [ ] Select and save AI refine
- [ ] Verify formatting (no ###, **)
- [ ] Check examples are localized
- [ ] Test with table/list questions

**API**
- [ ] GET /api/departments/
- [ ] GET /api/departments/1/courses/
- [ ] GET /api/courses/1/topics/
- [ ] GET /api/topics/1/
- [ ] POST /topics/1/generate-ai/
- [ ] GET /ai-status/

### Automated Tests
```bash
python manage.py test
```

---

## 🚢 Deployment

### Option 1: Render (Recommended)

1. **Create Render account** at render.com

2. **Create PostgreSQL database**
   - Click "New +" → PostgreSQL
   - Copy DATABASE_URL

3. **Create Web Service**
   - Click "New +" → Web Service
   - Connect GitHub repo
   - Settings:
     ```
     Build Command: pip install -r requirements.txt
     Start Command: gunicorn scanner.wsgi:application
     ```

4. **Environment Variables**
   ```
   DJANGO_SECRET_KEY=<generate-random-key>
   DEBUG=False
   DATABASE_URL=<from-step-2>
   ALLOWED_HOSTS=your-app.onrender.com
   GEMINI_API_KEY=<your-key>
   GROQ_API_KEY=<your-key>
   CORS_ALLOWED_ORIGINS=https://your-pwa.vercel.app
   CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Automatic deploys on git push

---

### Option 2: Railway

```bash
railway login
railway init
railway up

# Add environment variables in Railway dashboard
```

---

### Option 3: Heroku

```bash
heroku create cafphy-backend
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set DJANGO_SECRET_KEY=...
heroku config:set GEMINI_API_KEY=...
heroku config:set GROQ_API_KEY=...

git push heroku main
heroku run python manage.py migrate
heroku run python manage.py seed_departments
```

---

## 🔒 Security

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure CORS properly (specific origins)
- [ ] Add CSRF_TRUSTED_ORIGINS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set secure cookie flags
- [ ] Enable HSTS headers
- [ ] Add rate limiting (future)
- [ ] Add authentication (future)

### Current Security Features

✅ CSRF protection enabled
✅ XSS protection enabled
✅ Clickjacking protection
✅ Secure cookies in production
✅ CORS configured
✅ HSTS headers (when DEBUG=False)

---

## 🐛 Troubleshooting

### "No module named 'scan'"
**Solution:**
```bash
# Make sure you're in the right directory
cd cafphy-backend
python manage.py runserver
```

### "No such table: scan_department"
**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### "GEMINI_API_KEY not found"
**Solution:**
```bash
# Check .env file exists
cat .env

# Or export manually
export GEMINI_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
```

### OCR not working
**Solution:**
1. Check Colab notebook is running
2. Update `COLAB_OCR_URL` in .env
3. Test: `curl <ngrok-url>/health`

### Groq 400 Error
**Solution:** Model detection will auto-select available model. If persists:
1. Check API key is valid
2. Check account has usage quota
3. Try different model in code

### Rate Limiting (429 errors)
**Solution:** Built-in retry with exponential backoff. Will automatically retry up to 8 times.

---

## 📖 Documentation

- **[PHASE1.md](PHASE1.md)** - Detailed migration guide
- **Django Docs** - https://docs.djangoproject.com/
- **Gemini API** - https://ai.google.dev/docs
- **Groq API** - https://console.groq.com/docs

---

## 🎯 Roadmap

### Current Phase ✅
- [x] Department system
- [x] AI refine (Gemini + Groq)
- [x] REST API
- [x] Localized examples
- [x] Clean formatting

### Future Phases 🚧
- [ ] User authentication
- [ ] Bulk AI generation
- [ ] PDF export
- [ ] Usage analytics
- [ ] Rate limiting
- [ ] Caching layer
- [ ] WebSocket support
- [ ] Background tasks (Celery)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

Educational use only.

---

## 👨‍💻 Support

- **Documentation**: PHASE1.md, README.md
- **Issues**: GitHub Issues
- **Email**: studycompanion@gmail.com

---

**Built with ❤️ for Liberian students at community colleges.**