# 🔐 Backend Admin Authentication System - Implementation Guide

## 📋 Overview
This system creates a **separate authentication layer** for backend administrators (you and your team) while keeping the existing PremiumUser system for frontend users untouched.

---

## 🚀 Step-by-Step Implementation

### **STEP 1: Update `core/models.py`**

Replace your entire `core/models.py` with the provided `AdminUser` model code.

**Key Points:**
- Custom user model extending `AbstractBaseUser`
- Includes username, full_name, password
- Completely separate from `PremiumUser`

---

### **STEP 2: Create `core/views.py`**

Create a new file `core/views.py` with the authentication views provided.

**This includes:**
- `admin_login` - Login page
- `admin_logout` - Logout functionality
- `account_settings` - Profile and password management
- `admin_password_reset` - Superuser-only password reset

---

### **STEP 3: Create `core/urls.py`**

Create a new file `core/urls.py` with the URL patterns provided.

---

### **STEP 4: Create Templates Directory**

Create these template files:

```
templates/
├── core/
│   ├── login.html                    ← Login page
│   ├── account_settings.html         ← Account management
│   └── admin_password_reset.html     ← Password reset (superuser only)
└── scan/
    └── partials/
        └── home.html                  ← Updated with account link
```

Copy the provided template code into each file.

---

### **STEP 5: Update `settings.py`**

Add these settings to your `settings.py`:

```python
# =========================
# Custom User Model
# =========================
AUTH_USER_MODEL = 'core.AdminUser'

# =========================
# Authentication URLs
# =========================
LOGIN_URL = 'core:admin_login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'core:admin_login'
```

---

### **STEP 6: Update Project URLs (`scanner/urls.py`)**

Update your main project `scanner/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('core.urls')),      # ADD THIS LINE
    path('', include('scan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### **STEP 7: Protect Your Views**

Update each view file in `scan/views_functions/` to add login protection:

#### Example: `scan/views_functions/home_views.py`

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='core:admin_login')
def home(request):
    """Main landing page with two options"""
    return render(request, 'scan/partials/home.html')
```

#### Files to Update:
- `home_views.py` - Add `@login_required` to `home`
- `scan_views.py` - Add to `scan_new`, `upload_and_extract`, `save_topic`
- `library_views.py` - Add to all views
- `topic_management_views.py` - Add to all views
- `course_management_views.py` - Add to all views
- `text_input_views.py` - Add to all views

#### **DO NOT PROTECT:**
- `api_views.py` - Keep these open for mobile app

---

### **STEP 8: Create Database Migrations**

**CRITICAL:** You need to delete your existing database and create a new one because you're changing the user model.

```bash
# 1. Delete existing database
rm db.sqlite3

# 2. Delete existing migrations from core app
rm core/migrations/0*.py

# 3. Create new migrations
python manage.py makemigrations core

# 4. Create migrations for other apps
python manage.py makemigrations

# 5. Apply all migrations
python manage.py migrate

# 6. Create your first admin user
python manage.py createsuperuser
```

**When creating superuser:**
- Username: `admin` (or your choice)
- Password: Your password (minimum 6 characters)

---

### **STEP 9: Update Premium Users URLs**

Update `premium_users/urls_patterns/admin_urls.py` to add login protection:

```python
from django.urls import path
from django.contrib.auth.decorators import login_required
from .. import views

admin_urlpatterns = [
    path('manage/', login_required(views.manage_premium_users, login_url='core:admin_login'), name='manage_users'),
    path("add/", login_required(views.add_premium_user, login_url='core:admin_login'), name="add_user"),
    path('send-topics/', login_required(views.send_premium_topics, login_url='core:admin_login'), name='send_topics'),
    path("delete-topic/<int:topic_id>/", login_required(views.delete_premium_topic, login_url='core:admin_login'), name="delete_premium_topic"),
    path('edit/<int:user_id>/', login_required(views.edit_premium_user, login_url='core:admin_login'), name='edit_user'),
    path('toggle/<int:user_id>/', login_required(views.toggle_user_status, login_url='core:admin_login'), name='toggle_status'),
    path('delete/<int:user_id>/', login_required(views.delete_premium_user, login_url='core:admin_login'), name='delete_user'),
]
```

---

## 🎯 Testing the System

### **Test 1: Access Without Login**
1. Start server: `python manage.py runserver`
2. Visit: `http://127.0.0.1:8000/`
3. **Expected:** Redirected to login page

### **Test 2: Login**
1. Enter your username and password
2. **Expected:** Redirected to home page

### **Test 3: Account Settings**
1. Click "⚙️ Account" button on home page
2. **Expected:** See profile and password change forms

### **Test 4: Password Change**
1. Fill in password change form
2. **Expected:** Success message, still logged in

### **Test 5: Admin Password Reset (Superuser Only)**
1. Visit account settings
2. Click "Reset User Passwords" under Admin Tools
3. **Expected:** Form to reset any user's password

### **Test 6: Logout**
1. Click logout button
2. **Expected:** Redirected to login page

### **Test 7: API Access (Should Remain Open)**
1. Visit: `http://127.0.0.1:8000/api/departments/`
2. **Expected:** JSON response (NO login required)

---

## 📁 File Structure Summary

```
your_project/
├── scanner/                    # Project folder
│   ├── settings.py            # ✏️ UPDATE: Add AUTH_USER_MODEL
│   └── urls.py                # ✏️ UPDATE: Add core.urls
│
├── core/                      # Core app
│   ├── models.py              # ✏️ REPLACE: Add AdminUser model
│   ├── views.py               # ✅ CREATE: Auth views
│   ├── urls.py                # ✅ CREATE: Auth URLs
│   └── migrations/            # 🔄 REGENERATE
│
├── scan/                      # Scan app
│   └── views_functions/       # ✏️ UPDATE: Add @login_required
│       ├── home_views.py
│       ├── scan_views.py
│       ├── library_views.py
│       ├── topic_management_views.py
│       ├── course_management_views.py
│       └── text_input_views.py
│
├── premium_users/             # Premium users app
│   └── urls_patterns/
│       └── admin_urls.py      # ✏️ UPDATE: Add @login_required
│
└── templates/
    ├── core/                  # ✅ CREATE
    │   ├── login.html
    │   ├── account_settings.html
    │   └── admin_password_reset.html
    └── scan/
        └── partials/
            └── home.html      # ✏️ UPDATE: Add account link
```

---

## 🔑 Key Features

### ✅ **What This System Does:**
- Creates separate admin authentication (different from PremiumUser)
- Protects all backend views with login
- Keeps API endpoints open for mobile app
- Allows password management
- Provides admin-only password reset

### ✅ **Access Levels:**
- **Regular Admin User:** Can login, change own password, manage content
- **Superuser:** All above + reset any user's password + Django admin access

### ✅ **Security:**
- Passwords are hashed (Django default)
- Session-based authentication
- CSRF protection on all forms
- Login required for all backend pages
- API endpoints remain open (no auth needed for frontend)

---

## 🆘 Troubleshooting

### **Problem: "No such table: core_adminuser"**
**Solution:** Run migrations again:
```bash
python manage.py migrate
```

### **Problem: "AdminUser is not defined"**
**Solution:** Make sure `AUTH_USER_MODEL = 'core.AdminUser'` is in settings.py

### **Problem: "Redirect loop at /login/"**
**Solution:** Check that you're using `login_url='core:admin_login'` in decorators

### **Problem: "Can't login to Django admin"**
**Solution:** Make sure your user is a superuser:
```bash
python manage.py createsuperuser
```

---

## 📝 Quick Reference

### **Login URL:**
`http://127.0.0.1:8000/auth/login/`

### **Account Settings URL:**
`http://127.0.0.1:8000/auth/account/`

### **Password Reset URL (Superuser only):**
`http://127.0.0.1:8000/auth/admin-reset-password/`

### **Create New Admin User (Command Line):**
```bash
python manage.py createsuperuser
```

---

## ✨ You're Done!

After following all steps:
1. ✅ All backend pages require login
2. ✅ API endpoints remain open for mobile app
3. ✅ You can manage your account
4. ✅ Superusers can reset passwords
5. ✅ Clean separation from PremiumUser system
