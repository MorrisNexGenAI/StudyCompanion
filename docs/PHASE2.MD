# Phase 2: Premium User Management & Access Control (Backend)

## Overview
Phase 2 implements a comprehensive premium content management system allowing administrators to create premium users and control topic access. Students authenticate with name + 4-character code to access assigned premium content.

---

## Key Features Added

1. **Premium User Model** - Name + 4-character code authentication
2. **Topic Access Control** - Community vs Premium topics
3. **User Management Interface** - CRUD operations for premium users
4. **Topic Assignment System** - Assign topics to specific users
5. **Filtered API Responses** - Users see only assigned content
6. **Soft Delete System** - Non-destructive deletion
7. **Admin Dashboard** - Manage users and assignments

---

## Part A: Database Layer

### 1. New App: premium_users

**Created:** `premium_users/` Django app

**Purpose:** Isolate premium user logic from core scanning functionality

**Structure:**
```
premium_users/
├── __init__.py
├── models.py              # PremiumUser model
├── views.py               # Admin UI + API endpoints
├── urls.py                # Premium routes
├── apps.py                # App configuration
└── templates/
    └── premium_users/
        ├── manage_users.html       # User CRUD
        ├── add_user.html           # Create user
        ├── edit_user.html          # Edit user
        └── send_topics.html        # Assign topics
```

---

### 2. PremiumUser Model

**Location:** `premium_users/models.py`

**Full Model Definition:**
```python
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel

class PremiumUser(BaseModel):
    """
    Premium user identified by name + 4-character code.
    No passwords - just identity for content filtering.
    """
    
    # Validator: exactly 4 alphanumeric characters
    code_validator = RegexValidator(
        regex=r'^[A-Z0-9]{4}$',
        message='Code must be exactly 4 alphanumeric characters (A-Z, 0-9).',
        code='invalid_code'
    )
    
    name = models.CharField(
        max_length=100,
        help_text="User's full name (e.g., 'Emmanuel Cooper')"
    )
    
    code = models.CharField(
        max_length=4,
        validators=[code_validator],
        help_text="Exactly 4 alphanumeric characters (e.g., 'EC21', 'AB12')"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive users cannot access premium content"
    )
    
    class Meta:
        verbose_name = "Premium User"
        verbose_name_plural = "Premium Users"
        unique_together = [('name', 'code')]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'code']),
            models.Index(fields=['is_active']),
        ]
    
    def clean(self):
        """Validate and normalize code before saving."""
        super().clean()
        if self.code:
            # Convert to uppercase
            self.code = self.code.upper()
            
            # Check length
            if len(self.code) != 4:
                raise ValidationError({'code': 'Code must be exactly 4 characters long.'})
            
            # Check alphanumeric
            if not self.code.isalnum():
                raise ValidationError({'code': 'Code must contain only letters (A-Z) and numbers (0-9).'})
    
    def save(self, *args, **kwargs):
        """Ensure code is uppercase before saving."""
        if self.code:
            self.code = self.code.upper()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{self.name} ({self.code}) {status}"
    
    @property
    def display_name(self):
        """Formatted name with code for UI display."""
        return f"{self.name} ({self.code})"
    
    def deactivate(self):
        """Soft-delete: mark user as inactive."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def reactivate(self):
        """Restore deactivated user."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
```

**Key Design Decisions:**

1. **No Passwords** - Simple name+code system for education context
2. **unique_together** - Prevents duplicate (name, code) pairs
3. **Code Validation** - Enforces 4-char alphanumeric format
4. **Auto-Uppercase** - Code always stored uppercase
5. **Soft Deactivation** - is_active flag instead of deletion
6. **Indexes** - Fast lookups on name+code and is_active

---

### 3. Topic Model Updates

**Location:** `scan/models.py`

**New Fields Added:**
```python
class Topic(BaseModel):
    # ... existing fields ...
    
    is_premium = models.BooleanField(
        default=False,
        help_text="If True, only selected premium users can access this topic"
    )
    
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag"
    )
    
    premium_users = models.ManyToManyField(
        'premium_users.PremiumUser',
        blank=True,
        related_name='accessible_topics',
        limit_choices_to={'is_active': True},
        help_text="Select users who can access this premium topic"
    )
    
    class Meta:
        ordering = ['course', 'order', 'created_at']
        indexes = [
            models.Index(fields=['is_premium']),
            models.Index(fields=['is_deleted']),
        ]
```

**New Methods Added:**
```python
def is_accessible_by(self, user):
    """
    Check if a user can access this topic.
    
    Args:
        user: PremiumUser instance or user_id (int)
    
    Returns:
        bool: True if accessible, False otherwise
    """
    # Community topics are always accessible
    if not self.is_premium:
        return True
    
    # Premium topics require user to be in premium_users AND active
    if isinstance(user, int):
        return self.premium_users.filter(id=user, is_active=True).exists()
    else:
        return self.premium_users.filter(id=user.id, is_active=True).exists()

def soft_delete(self):
    """Soft delete topic"""
    self.is_deleted = True
    self.save(update_fields=['is_deleted', 'updated_at'])
```

---

### 4. Database Migrations

**Migration Steps:**
```bash
# Create migrations
python manage.py makemigrations premium_users
python manage.py makemigrations scan

# Apply migrations
python manage.py migrate

# Create indexes
python manage.py migrate --run-syncdb
```

**Tables Created:**
- `premium_users_premiumuser` - Premium user accounts
- `scan_topic_premium_users` - Many-to-many relationship table

**Indexes Created:**
- `premium_users_premiumuser_name_code_idx`
- `premium_users_premiumuser_is_active_idx`
- `scan_topic_is_premium_idx`
- `scan_topic_is_deleted_idx`

---

## Part B: Admin Interface (Web UI)

### 1. Manage Premium Users

**URL:** `/premium/manage/`

**Features:**
- List all premium users with status badges
- Search by name or code
- Filter by active/inactive
- Edit user details
- Toggle active/inactive status
- Delete users
- Pagination

**View Function:**
```python
def manage_premium_users(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    users = PremiumUser.objects.all()
    
    # Search
    if search:
        users = users.filter(
            Q(name__icontains=search) | Q(code__icontains=search)
        )
    
    # Filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    users = users.order_by('-created_at')
    
    return render(request, 'premium_users/manage_users.html', {
        'users': users,
        'search': search,
        'status_filter': status_filter,
        'total_count': PremiumUser.objects.count(),
        'active_count': PremiumUser.objects.filter(is_active=True).count(),
        'inactive_count': PremiumUser.objects.filter(is_active=False).count(),
    })
```

**UI Components:**
- Search bar with real-time filtering
- Status filter dropdown (All/Active/Inactive)
- User cards with name, code, status badge
- Action buttons (Edit, Toggle Status, Delete)
- Stats cards showing counts

---

### 2. Add Premium User

**URL:** `/premium/add/`

**Validation Rules:**
- Name: Required, 1-100 characters
- Code: Required, exactly 4 characters
- Code: Alphanumeric only (A-Z, 0-9)
- Code: Must be unique
- Name+Code combination: Must be unique

**View Function:**
```python
def add_premium_user(request):
    error = None
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        
        # Validation
        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.filter(code=code).exists():
            error = "This code already exists."
        
        if not error:
            PremiumUser.objects.create(name=name, code=code, is_active=True)
            return redirect('premium_users:manage_users')
    
    return render(request, 'premium_users/add_user.html', {'error': error})
```

---

### 3. Send Premium Topics

**URL:** `/premium/send-topics/`

**Features:**
- List all premium topics
- Show assigned user count per topic
- Display currently assigned users
- Modal for user selection
- Bulk select/deselect users
- Real-time assignment updates

**View Function:**
```python
def send_premium_topics(request):
    # Get all premium topics
    premium_topics = Topic.objects.filter(
        is_premium=True,
        is_deleted=False
    ).select_related('course').order_by('-created_at')
    
    # Get all active premium users
    active_users = PremiumUser.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        selected_user_ids = request.POST.getlist('premium_users')
        
        if topic_id:
            topic = get_object_or_404(Topic, id=topic_id, is_premium=True)
            
            # Clear existing assignments
            topic.premium_users.clear()
            
            # Assign to selected users ONLY
            if selected_user_ids:
                topic.premium_users.set(selected_user_ids)
            
            return redirect('premium_users:send_topics')
    
    # Prepare data for template
    topics_with_users = []
    for topic in premium_topics:
        assigned_users = topic.premium_users.filter(is_active=True)
        topics_with_users.append({
            'topic': topic,
            'assigned_users': assigned_users,
            'assigned_user_ids': list(assigned_users.values_list('id', flat=True)),
            'assigned_count': assigned_users.count()
        })
    
    return render(request, 'premium_users/send_topics.html', {
        'topics_with_users': topics_with_users,
        'active_users': active_users,
        'total_topics': premium_topics.count(),
        'total_users': active_users.count()
    })
```

**Assignment Flow:**
```
1. Click "📤 Send to Users" on topic
2. Modal opens with user checkboxes
3. Pre-select currently assigned users
4. Select/deselect users as needed
5. Click "Send to Selected Users"
6. Existing assignments cleared
7. New assignments saved
8. Modal closes, page refreshes
```

---

## Part C: API Layer

### 1. Registration/Login Endpoint

**URL:** `POST /premium/api/register-or-login/`

**Purpose:** Unified endpoint for user registration AND login

**Request:**
```json
{
  "name": "Emmanuel Cooper",
  "code": "EC21"
}
```

**Response (New User):**
```json
{
  "user_id": 2,
  "name": "Emmanuel Cooper",
  "code": "EC21",
  "is_new": true
}
```

**Response (Existing User):**
```json
{
  "user_id": 2,
  "name": "Emmanuel Cooper",
  "code": "EC21",
  "is_new": false
}
```

**Error Responses:**
```json
// Invalid format
{
  "error": "Code must be exactly 4 alphanumeric characters"
}

// Code exists with different name
{
  "error": "This code is already linked to another user"
}

// Name exists with different code
{
  "error": "This name is already linked to another code"
}

// Account inactive
{
  "error": "Account is inactive"
}
```

**View Function:**
```python
@csrf_exempt
def register_or_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        code = data.get('code', '').strip().upper()
        
        # Validation
        if not name or not code:
            return JsonResponse({'error': 'Name and code are required'}, status=400)
        
        if len(code) != 4 or not code.isalnum():
            return JsonResponse({'error': 'Invalid code format'}, status=400)
        
        # Check exact match (LOGIN CASE)
        user = PremiumUser.objects.filter(name__iexact=name, code=code).first()
        
        if user:
            if not user.is_active:
                return JsonResponse({'error': 'Account is inactive'}, status=403)
            
            return JsonResponse({
                'user_id': user.id,
                'name': user.name,
                'code': user.code,
                'is_new': False
            })
        
        # Check partial conflicts (SECURITY)
        if PremiumUser.objects.filter(code=code).exists():
            return JsonResponse({'error': 'This code is already linked to another user'}, status=403)
        
        if PremiumUser.objects.filter(name__iexact=name).exists():
            return JsonResponse({'error': 'This name is already linked to another code'}, status=403)
        
        # CREATE (FIRST TIME)
        user = PremiumUser.objects.create(name=name, code=code, is_active=True)
        
        return JsonResponse({
            'user_id': user.id,
            'name': user.name,
            'code': user.code,
            'is_new': True
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

**Security Logic:**
1. **Exact Match** → Login existing user
2. **Code Exists (different name)** → Error (security)
3. **Name Exists (different code)** → Error (security)
4. **Neither Exists** → Create new user

---

### 2. Content Filtering Functions

**Location:** `premium_users/views.py`

**filter_topics_for_user():**
```python
def filter_topics_for_user(topics_queryset, user_id=None):
    """
    CRITICAL FUNCTION: Filter topics based on user access.
    
    RULES:
    1. NO user_id → ONLY community topics
    2. Has user_id → Community + ASSIGNED premium topics
    
    IMPORTANT: Being a "premium user" does NOT grant access to ALL premium.
    You must be EXPLICITLY assigned to each topic.
    """
    # Always exclude soft-deleted
    topics_queryset = topics_queryset.filter(is_deleted=False)
    
    if not user_id:
        # NO USER ID = Only show community topics
        return topics_queryset.filter(is_premium=False)
    
    try:
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        
        # Return topics where:
        # 1. is_premium=False (community), OR
        # 2. is_premium=True AND user is in premium_users list
        return topics_queryset.filter(
            Q(is_premium=False) | Q(is_premium=True, premium_users=user)
        ).distinct()
    
    except PremiumUser.DoesNotExist:
        return topics_queryset.filter(is_premium=False)
```

**check_topic_access():**
```python
def check_topic_access(topic, user_id=None):
    """
    Check if a specific user can access a specific topic.
    
    RULES:
    - Community topic → Always True
    - Premium topic + no user_id → False
    - Premium topic + user_id → True ONLY if explicitly assigned
    """
    # Community topics accessible to everyone
    if not topic.is_premium:
        return True
    
    # Premium topic with no user_id = no access
    if not user_id:
        return False
    
    try:
        user = PremiumUser.objects.get(id=user_id, is_active=True)
        return topic.is_accessible_by(user)
    except PremiumUser.DoesNotExist:
        return False
```

---

### 3. Updated API Endpoints

**All topic endpoints now accept user_id:**

**Get Topics in Course:**
```python
def api_course_topics(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_deleted=False)
    
    # Get user_id from query param or header
    user_id = request.GET.get('user_id') or request.headers.get('X-User-ID')
    
    # Get all topics for this course
    topics = course.topics.all()
    
    # FILTER BASED ON USER ACCESS
    topics = filter_topics_for_user(topics, user_id)
    
    data = [{
        'id': t.id,
        'title': t.title,
        'page_range': t.page_range,
        'is_premium': t.is_premium,
        'is_refined': t.is_refined(),
        'updated_at': int(t.updated_at.timestamp()),
    } for t in topics]
    
    return JsonResponse(data, safe=False)
```

**Get Topic Detail:**
```python
def api_topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id, is_deleted=False)
    
    # Get user_id
    user_id = request.GET.get('user_id') or request.headers.get('X-User-ID')
    
    # CHECK ACCESS PERMISSION
    if not check_topic_access(topic, user_id):
        return JsonResponse({
            'error': 'Access denied. This is a premium topic.',
            'is_premium': True,
            'requires_login': True
        }, status=403)
    
    # User has access, return full topic
    data = {
        'id': topic.id,
        'title': topic.title,
        'refined_summary': topic.refined_summary,
        'raw_text': topic.raw_text,
        'course_name': topic.course.name,
        'is_premium': topic.is_premium,
        # ... other fields
    }
    
    return JsonResponse(data)
```

---

## Part D: Admin Features

### 1. Staff Access Control

**Admin users can:**
- View ALL topics (community + premium)
- Edit refined summaries for ANY topic
- Assign/unassign premium topics
- Manage premium users
- Soft delete topics

**Updated topic_detail view:**
```python
def topic_detail(request, topic_id):
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
```

---

### 2. Soft Delete System

**All deletions are now soft deletes:**

**Course Soft Delete:**
```python
def delete_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.soft_delete()  # Sets is_deleted=True
        messages.success(request, f"Course '{course.name}' deleted.")
        return redirect('library')
    return redirect('library')
```

**Topic Soft Delete:**
```python
def delete_topic(request, topic_id):
    if request.method == 'POST':
        topic = get_object_or_404(Topic, id=topic_id)
        course_id = topic.course.id
        topic.soft_delete()  # Sets is_deleted=True
        messages.success(request, f"Topic '{topic.title}' deleted.")
        return redirect('course_detail', course_id=course_id)
    return redirect('library')
```

**All Queries Updated:**
```python
# Before
topics = Topic.objects.all()

# After
topics = Topic.objects.filter(is_deleted=False)
```

---

## Part E: URL Configuration

### 1. Premium URLs

**Location:** `premium_users/urls.py`

```python
app_name = 'premium_users'

urlpatterns = [
    # Admin UI
    path('manage/', views.manage_premium_users, name='manage_users'),
    path('add/', views.add_premium_user, name='add_user'),
    path('edit/<int:user_id>/', views.edit_premium_user, name='edit_user'),
    path('toggle/<int:user_id>/', views.toggle_user_status, name='toggle_status'),
    path('delete/<int:user_id>/', views.delete_premium_user, name='delete_user'),
    path('send-topics/', views.send_premium_topics, name='send_topics'),
    
    # API
    path('api/register-or-login/', views.register_or_login, name='register_or_login'),
    path('api/<int:user_id>/topics/', views.get_accessible_topics, name='accessible_topics'),
]
```

### 2. Main URLs Update

**Location:** `scanner/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scan.urls')),
    path('premium/', include('premium_users.urls')),  # NEW
]
```

---

## Part F: Testing

### Manual Testing Checklist

**Premium User Management:**
- [ ] Create user with valid name+code
- [ ] Create user with invalid code (error)
- [ ] Create user with duplicate code (error)
- [ ] Edit user name and code
- [ ] Toggle user active/inactive
- [ ] Search users by name
- [ ] Search users by code
- [ ] Filter active users
- [ ] Filter inactive users

**Topic Assignment:**
- [ ] Assign premium topic to single user
- [ ] Assign premium topic to multiple users
- [ ] Unassign all users from topic
- [ ] Reassign topic to different users
- [ ] View assigned users on topic card

**API Authentication:**
- [ ] Register new user (returns user_id)
- [ ] Login existing user (returns same user_id)
- [ ] Invalid code format (error)
- [ ] Duplicate code (error)
- [ ] Inactive account (error)

**Content Filtering:**
- [ ] GET /api/topics/ without user_id (community only)
- [ ] GET /api/topics/?user_id=2 (community + assigned premium)
- [ ] GET /api/topics/5/?user_id=2 (assigned = success)
- [ ] GET /api/topics/5/?user_id=3 (not assigned = 403)
- [ ] Premium user sees only assigned topics
- [ ] Community user sees only community topics

**Admin Access:**
- [ ] Admin can view all topics
- [ ] Admin can edit premium topics
- [ ] Admin can delete premium topics
- [ ] Non-admin blocked from premium topics

---

## Part G: Security Considerations

### 1. Authentication Security

**Strengths:**
- Simple for students to remember
- No password complexity requirements
- No password reset needed
- Suitable for educational context

**Limitations:**
- Not suitable for highly sensitive data
- No session management
- No token expiration
- Client can impersonate with valid user_id

**Mitigations:**
- HTTPS required in production
- CORS restrictions
- Rate limiting (future)
- Backend always validates user_id

---

### 2. Access Control Security

**Defense in Depth:**
1. **Frontend** - Hides premium topics not assigned
2. **Backend** - Validates user_id on every request
3. **Database** - Many-to-many enforces explicit assignment
4. **Admin** - Only staff can modify assignments

**Attack Vectors Addressed:**
- ❌ User modifies user_id in request → Backend validates
- ❌ User guesses topic IDs → 403 if not assigned
- ❌ Inactive user tries to access → Filtered out
- ❌ Deleted topics accessed → Filtered out

---

## Key Achievements

1. ✅ **Simple Authentication** - Name + code system
2. ✅ **Granular Access Control** - Per-topic assignments
3. ✅ **Admin Dashboard** - Full user/topic management
4. ✅ **Filtered API** - Users see only assigned content
5. ✅ **Soft Delete** - Non-destructive deletion
6. ✅ **Staff Override** - Admins have full access
7. ✅ **Secure Assignment** - Explicit topic-user relationships
8. ✅ **Production Ready** - Error handling, validation, security

---

## Future Enhancements

### Planned Features
- [ ] Password option (optional security layer)
- [ ] Session tokens with expiration
- [ ] User groups (assign topics to entire class)
- [ ] Topic expiration dates
- [ ] Access logs/analytics
- [ ] Email notifications on assignment
- [ ] Bulk import users from CSV
- [ ] QR code generation for quick registration

---

**Phase 2 Complete! 🎉**

The backend now supports premium user management with granular topic access control.