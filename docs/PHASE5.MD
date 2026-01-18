# 🚀 PHASE 5 - Backend Department Integration for Premium Users

## 📋 Overview
Add department field to PremiumUser model and update all related views, templates, and APIs to support department-based filtering.

---

## ✅ STEP 1: Update PremiumUser Model

**File:** `premium_users/models.py`

**REPLACE THE ENTIRE MODEL** with this:

```python
"""
PremiumUser model - Premium user identified by name + 4-character code + department
"""
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel


class PremiumUser(BaseModel):
    """
    Premium user identified by name + 4-character code + department.
    No passwords, no authentication - just identity for content filtering.
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
    
    # NEW FIELD: Department selection
    department = models.ForeignKey(
        'scan.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='premium_users',
        help_text="User's department - filters courses and topics"
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
            models.Index(fields=['department']),  # NEW INDEX
        ]
    
    def clean(self):
        """Validate and normalize code before saving."""
        super().clean()
        if self.code:
            self.code = self.code.upper()
            if len(self.code) != 4:
                raise ValidationError({
                    'code': 'Code must be exactly 4 characters long.'
                })
            if not self.code.isalnum():
                raise ValidationError({
                    'code': 'Code must contain only letters (A-Z) and numbers (0-9).'
                })
    
    def save(self, *args, **kwargs):
        """Ensure code is uppercase before saving."""
        if self.code:
            self.code = self.code.upper()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        dept_name = f" - {self.department.name}" if self.department else ""
        return f"{self.name} ({self.code}){dept_name} {status}"
    
    @property
    def display_name(self):
        """Formatted name with code for UI display."""
        return f"{self.name} ({self.code})"
    
    @property
    def display_full(self):
        """Full display with department."""
        dept = f" - {self.department.name}" if self.department else " - No Department"
        return f"{self.name} ({self.code}){dept}"
    
    def deactivate(self):
        """Soft-delete: mark user as inactive."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def reactivate(self):
        """Restore deactivated user."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
```

---

## ✅ STEP 2: Update API Views

**File:** `premium_users/views_functions/api_views.py`

**UPDATE THREE FUNCTIONS:**

### **Function 1: `register_or_login`**

Replace the entire function:

```python
@csrf_exempt
def register_or_login(request):
    """API endpoint for user registration/login with department selection"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        import json
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        code = data.get('code', '').strip().upper()
        department_id = data.get('department_id')  # NEW FIELD

        # Validation
        if not name or not code:
            return JsonResponse({'error': 'Name and code are required'}, status=400)

        if len(code) != 4 or not code.isalnum():
            return JsonResponse({'error': 'Invalid code format'}, status=400)

        # Validate department
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({'error': 'Invalid department selected'}, status=400)

        # Check exact match (LOGIN CASE)
        user = PremiumUser.objects.filter(
            name__iexact=name,
            code=code
        ).first()

        if user:
            if not user.is_active:
                return JsonResponse({'error': 'Account is inactive'}, status=403)

            # Update department if provided and different
            if department and user.department != department:
                user.department = department
                user.save(update_fields=['department', 'updated_at'])

            return JsonResponse({
                'user_id': user.id,
                'name': user.name,
                'code': user.code,
                'department_id': user.department.id if user.department else None,
                'department_name': user.department.name if user.department else None,
                'is_new': False
            })

        # Check partial conflicts (SECURITY)
        if PremiumUser.objects.filter(code=code).exists():
            return JsonResponse({
                'error': 'This code is already linked to another user'
            }, status=403)

        if PremiumUser.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'error': 'This name is already linked to another code'
            }, status=403)

        # CREATE (FIRST TIME)
        user = PremiumUser.objects.create(
            name=name,
            code=code,
            department=department,
            is_active=True
        )

        return JsonResponse({
            'user_id': user.id,
            'name': user.name,
            'code': user.code,
            'department_id': user.department.id if user.department else None,
            'department_name': user.department.name if user.department else None,
            'is_new': True
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### **Function 2: ADD NEW - `get_departments_list`**

Add this NEW function at the end of `api_views.py`:

```python
@csrf_exempt
def get_departments_list(request):
    """API endpoint to get all available departments for registration"""
    from scan.models import Department
    
    departments = Department.objects.all().order_by('name')
    
    data = [{
        'id': d.id,
        'name': d.name
    } for d in departments]
    
    return JsonResponse({
        'departments': data
    })
```

### **Function 3: OPTIONAL - Update `get_accessible_topics`**

If you want department filtering for topics (recommended), replace this function:

```python
def get_accessible_topics(request, user_id):
    """
    Returns topics filtered by:
    1. User's department (only courses in their department)
    2. Community topics (everyone can see)
    3. Premium topics where user is explicitly assigned
    """
    user = get_object_or_404(PremiumUser, id=user_id, is_active=True)

    # If user has no department, return all topics or empty (your choice)
    if not user.department:
        return JsonResponse({
            'user': {
                'id': user.id,
                'name': user.name,
                'code': user.code,
                'department': None
            },
            'topics': [],
            'message': 'Please select a department to view topics'
        })

    # Get all topics from courses in user's department
    from scan.models import Topic
    department_topics = Topic.objects.filter(
        course__departments=user.department,
        is_deleted=False
    )

    # Filter by access rules
    community_topics = department_topics.filter(is_premium=False)
    premium_topics = department_topics.filter(
        is_premium=True,
        premium_users=user
    )

    # Combine both sets
    topics = (community_topics | premium_topics).distinct().order_by('-created_at')

    data = [{
        'id': t.id,
        'title': t.title,
        'is_premium': t.is_premium,
        'course_id': t.course.id,
        'course_name': t.course.name,
        'page_range': t.page_range,
    } for t in topics]

    return JsonResponse({
        'user': {
            'id': user.id,
            'name': user.name,
            'code': user.code,
            'department_id': user.department.id,
            'department_name': user.department.name
        },
        'topics': data
    })
```

---

## ✅ STEP 3: Update User Management Views

**File:** `premium_users/views_functions/user_management_views.py`

### **Update 1: `manage_premium_users`**

Add department filter. Find this section and update:

```python
def manage_premium_users(request):
    """Main page to view/edit/delete premium users."""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    department_filter = request.GET.get('department', 'all')  # NEW LINE

    users = PremiumUser.objects.select_related('department').all()  # UPDATED

    if search:
        users = users.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    # NEW: Department filter
    if department_filter != 'all':
        if department_filter == 'none':
            users = users.filter(department__isnull=True)
        else:
            users = users.filter(department_id=department_filter)

    users = users.order_by('-created_at')

    # NEW: Get all departments for filter dropdown
    from scan.models import Department
    all_departments = Department.objects.all().order_by('name')

    context = {
        'users': users,
        'search': search,
        'status_filter': status_filter,
        'department_filter': department_filter,  # NEW
        'all_departments': all_departments,  # NEW
        'total_count': PremiumUser.objects.count(),
        'active_count': PremiumUser.objects.filter(is_active=True).count(),
        'inactive_count': PremiumUser.objects.filter(is_active=False).count(),
    }

    return render(request, 'premium_users/manage_users.html', context)
```

### **Update 2: `add_premium_user`**

Add department field handling:

```python
def add_premium_user(request):
    """Create a new premium user (custom page)."""
    error = None
    
    # NEW: Get all departments
    from scan.models import Department
    all_departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        department_id = request.POST.get('department')  # NEW LINE

        # Validation
        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.filter(code=code).exists():
            error = "This code already exists."

        # NEW: Validate department
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                error = "Invalid department selected."

        if not error:
            PremiumUser.objects.create(
                name=name,
                code=code,
                department=department,  # NEW
                is_active=True
            )
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/add_user.html', {
        'error': error,
        'all_departments': all_departments  # NEW
    })
```

### **Update 3: `edit_premium_user`**

Add department field handling:

```python
def edit_premium_user(request, user_id):
    """Edit an existing premium user"""
    user = get_object_or_404(PremiumUser, id=user_id)
    error = None
    
    # NEW: Get all departments
    from scan.models import Department
    all_departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        department_id = request.POST.get('department')  # NEW LINE

        if not name or not code:
            error = "Name and code are required."
        elif len(code) != 4:
            error = "Code must be exactly 4 characters."
        elif not code.isalnum():
            error = "Code must contain only letters and numbers."
        elif PremiumUser.objects.exclude(id=user.id).filter(code=code).exists():
            error = "This code already exists."

        # NEW: Validate department
        department = None
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                error = "Invalid department selected."

        if not error:
            user.name = name
            user.code = code
            user.department = department  # NEW
            user.save()
            return redirect('premium_users:manage_users')

    return render(request, 'premium_users/edit_user.html', {
        'user': user,
        'error': error,
        'all_departments': all_departments  # NEW
    })
```

---

## ✅ STEP 4: Update URL Patterns

**File:** `premium_users/urls_patterns/api_urls.py`

Add the new departments endpoint:

```python
from django.urls import path
from ..views_functions import api_views

api_urlpatterns = [
    path('api/register-or-login/', api_views.register_or_login, name='api_register'),
    path('api/users/<int:user_id>/topics/', api_views.get_accessible_topics, name='api_user_topics'),
    path('api/departments/', api_views.get_departments_list, name='api_departments_list'),  # NEW
]
```

---

## ✅ STEP 5: Update Templates

### **Template 1: `premium_users/templates/premium_users/add_user.html`**

Add department dropdown after code field:

```html
<!-- Code Field -->
<div>
    <label class="block text-gray-700 font-bold mb-2">Personal Code</label>
    <input type="text"
           name="code"
           required
           maxlength="4"
           pattern="[A-Za-z0-9]{4}"
           class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none font-mono text-lg uppercase"
           placeholder="e.g., EC21"
           style="text-transform: uppercase;">
    <p class="text-sm text-gray-500 mt-1">
        Exactly 4 alphanumeric characters (A–Z, 0–9)
    </p>
</div>

<!-- NEW: Department Field -->
<div>
    <label class="block text-gray-700 font-bold mb-2">Department</label>
    <select name="department"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:outline-none">
        <option value="">-- Select Department (Optional) --</option>
        {% for dept in all_departments %}
        <option value="{{ dept.id }}">{{ dept.name }}</option>
        {% endfor %}
    </select>
    <p class="text-sm text-gray-500 mt-1">
        Users can only access courses from their department
    </p>
</div>
```

### **Template 2: `premium_users/templates/premium_users/edit_user.html`**

Add department dropdown after code field:

```html
<!-- Code Field -->
<div>
    <label class="block text-gray-700 font-bold mb-2">Personal Code</label>
    <input type="text" 
           name="code" 
           value="{{ user.code }}" 
           required
           maxlength="4"
           pattern="[A-Za-z0-9]{4}"
           class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none font-mono text-lg uppercase"
           placeholder="e.g., EC21"
           style="text-transform: uppercase;">
    <p class="text-sm text-gray-500 mt-1">Exactly 4 alphanumeric characters (A-Z, 0-9)</p>
</div>

<!-- NEW: Department Field -->
<div>
    <label class="block text-gray-700 font-bold mb-2">Department</label>
    <select name="department"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none">
        <option value="">-- Select Department (Optional) --</option>
        {% for dept in all_departments %}
        <option value="{{ dept.id }}" {% if user.department and user.department.id == dept.id %}selected{% endif %}>
            {{ dept.name }}
        </option>
        {% endfor %}
    </select>
    <p class="text-sm text-gray-500 mt-1">
        Users can only access courses from their department
    </p>
</div>
```

### **Template 3: `premium_users/templates/premium_users/manage_users.html`**

#### **Add department filter in search bar:**

After the Status Filter dropdown, add:

```html
<!-- Status Filter -->
<div>
    <select name="status" 
            class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none">
        <option value="all" {% if status_filter == 'all' %}selected{% endif %}>All Status</option>
        <option value="active" {% if status_filter == 'active' %}selected{% endif %}>✓ Active</option>
        <option value="inactive" {% if status_filter == 'inactive' %}selected{% endif %}>✗ Inactive</option>
    </select>
</div>

<!-- NEW: Department Filter -->
<div>
    <select name="department"
            class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none">
        <option value="all" {% if department_filter == 'all' %}selected{% endif %}>All Departments</option>
        <option value="none" {% if department_filter == 'none' %}selected{% endif %}>No Department</option>
        {% for dept in all_departments %}
        <option value="{{ dept.id }}" {% if department_filter == dept.id|stringformat:"s" %}selected{% endif %}>
            {{ dept.name }}
        </option>
        {% endfor %}
    </select>
</div>
```

#### **Add department column in table:**

In the table header, add after Code column:

```html
<th class="text-left py-3 px-4 font-bold text-gray-700">Code</th>
<th class="text-left py-3 px-4 font-bold text-gray-700">Department</th>  <!-- NEW -->
<th class="text-center py-3 px-4 font-bold text-gray-700">Status</th>
```

In the table body, add after Code cell:

```html
<!-- Code -->
<td class="py-3 px-4">
    <span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full font-mono font-bold">
        {{ user.code }}
    </span>
</td>

<!-- NEW: Department -->
<td class="py-3 px-4">
    {% if user.department %}
    <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
        {{ user.department.name }}
    </span>
    {% else %}
    <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
        No Department
    </span>
    {% endif %}
</td>
```

---

## ✅ STEP 6: Create and Run Migration

```bash
# Create migration
python manage.py makemigrations premium_users

# Review the migration (should show adding department field)
python manage.py showmigrations premium_users

# Apply migration
python manage.py migrate premium_users
```

Expected output:
```
Migrations for 'premium_users':
  premium_users/migrations/0XXX_add_department.py
    - Add field department to premiumuser
```

---

## ✅ STEP 7: Test Everything

### **Test 1: API - Register with Department**
```bash
curl -X POST http://localhost:8000/premium/api/register-or-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "code": "TU01",
    "department_id": 1
  }'
```

Expected response:
```json
{
  "user_id": 1,
  "name": "Test User",
  "code": "TU01",
  "department_id": 1,
  "department_name": "Computer Science",
  "is_new": true
}
```

### **Test 2: API - Get Departments**
```bash
curl http://localhost:8000/premium/api/departments/
```

Expected response:
```json
{
  "departments": [
    {"id": 1, "name": "Computer Science"},
    {"id": 2, "name": "Engineering"}
  ]
}
```

### **Test 3: Web - Add User with Department**
1. Visit `/premium/users/add/`
2. Fill in name and code
3. Select department from dropdown
4. Submit
5. Verify user created with department

### **Test 4: Web - Filter by Department**
1. Visit `/premium/users/manage/`
2. Select department from filter dropdown
3. Click Filter
4. Verify only users from that department shown

---

## ✅ DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] Model updated with department field
- [ ] Migrations created and applied locally
- [ ] API views updated (register, departments list)
- [ ] User management views updated (add, edit, manage)
- [ ] URL patterns updated
- [ ] All 3 templates updated (add, edit, manage)
- [ ] Tested locally - all features work
- [ ] Commit all changes to git
- [ ] Push to repository
- [ ] Run migrations on production:
  ```bash
  python manage.py migrate premium_users
  ```

---

## 🎯 WHAT THIS PHASE ACHIEVES

After completing Phase 5:

✅ **PremiumUser Model:**
- Has department field (optional)
- Department filters accessible topics
- Department shown in admin interface

✅ **API Endpoints:**
- Register/login accepts department_id
- New endpoint to get all departments
- Topics filtered by user's department

✅ **Web Interface:**
- Add user form has department dropdown
- Edit user form can change department
- Manage page filters by department
- Department column in users table

✅ **Data Flow:**
- Mobile app → Selects department → Sends to backend
- Backend → Filters topics by department → Sends to mobile
- Admin → Assigns department → Users see filtered content

---

## 🆘 TROUBLESHOOTING

### **Migration fails:**
```
django.db.utils.IntegrityError: FOREIGN KEY constraint failed
```
**Fix:** Department model doesn't exist. Check `scan.Department` exists.

### **API returns 500 error:**
```
Department matching query does not exist
```
**Fix:** Create departments in Django admin first.

### **Templates not showing dropdown:**
```
TemplateSyntaxError: Invalid block tag
```
**Fix:** Check `{% for dept in all_departments %}` is correct.

### **Filter not working:**
```
No users shown after filtering
```
**Fix:** Check `department_filter` in context and template.

---

## ✅ SUCCESS CRITERIA

You'll know Phase 5 is complete when:

1. ✅ Migration applied successfully
2. ✅ API returns departments list
3. ✅ Register API accepts department_id
4. ✅ Add user form has department dropdown
5. ✅ Edit user form shows selected department
6. ✅ Manage page filters by department
7. ✅ Department column shows in users table
8. ✅ No errors in logs

**Phase 5 Complete! 🎉**