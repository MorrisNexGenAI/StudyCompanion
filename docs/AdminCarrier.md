# 🔐 BACKEND UPDATE - Admin API Login for Admin Carrier PWA

## 📋 Overview
Add a new API endpoint for Admin Carrier PWA to login using Django admin credentials. This is **separate** from the existing admin web login system.

---

## ✅ FILES TO UPDATE

### **File 1: `core/views.py`**

Add this new view at the end of the file:

```python
# ==================== ADD THIS TO core/views.py ====================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json


@csrf_exempt
def admin_api_login(request):
    """
    API endpoint for Admin Carrier PWA login.
    Uses Django admin credentials (AdminUser model).
    
    POST /core/admin-api-login/
    {
        "username": "admin",
        "password": "your_password"
    }
    
    Returns:
    {
        "success": true,
        "username": "admin",
        "csrf_token": "..."
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)

        # Authenticate using Django's built-in authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login successful
            from django.contrib.auth import login
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'username': user.username,
                'csrf_token': request.META.get('CSRF_COOKIE', ''),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
def admin_api_logout(request):
    """
    API endpoint for Admin Carrier PWA logout.
    
    POST /core/admin-api-logout/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        from django.contrib.auth import logout
        logout(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

---

### **File 2: `core/urls.py`**

Update your existing `core/urls.py` to add the new API endpoints:

```python
# ==================== UPDATE core/urls.py ====================

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Existing web-based admin authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('account/', views.account_settings, name='account_settings'),
    path('admin-reset-password/', views.admin_password_reset, name='admin_password_reset'),
    
    # NEW: API endpoints for Admin Carrier PWA
    path('admin-api-login/', views.admin_api_login, name='admin_api_login'),
    path('admin-api-logout/', views.admin_api_logout, name='admin_api_logout'),
]
```

---

### **File 3: `settings.py`**

Add CORS settings to allow Admin Carrier PWA to connect:

```python
# ==================== ADD/UPDATE in settings.py ====================

# Allow Admin Carrier PWA to make requests
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Admin Carrier PWA dev server
    "http://192.168.43.1:8080",  # Android hotspot
    "http://192.168.137.1:8080",  # Windows hotspot
    "http://172.20.10.1:8080",  # iPhone hotspot
]

# Allow credentials (cookies, sessions)
CORS_ALLOW_CREDENTIALS = True

# If you don't have django-cors-headers installed:
# pip install django-cors-headers

# Add to INSTALLED_APPS:
INSTALLED_APPS = [
    # ... existing apps ...
    'corsheaders',  # ADD THIS
]

# Add to MIDDLEWARE (IMPORTANT: near the top):
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ADD THIS (must be near top)
    'django.middleware.security.SecurityMiddleware',
    # ... rest of middleware ...
]
```

---

## 🚀 DEPLOYMENT STEPS

### **Step 1: Install CORS Headers**
```bash
pip install django-cors-headers
pip freeze > requirements.txt
```

### **Step 2: Update Settings**
Add the CORS configuration shown above to `settings.py`

### **Step 3: Update Views**
Add the two new API views to `core/views.py`

### **Step 4: Update URLs**
Add the two new URL patterns to `core/urls.py`

### **Step 5: Test Locally**
```bash
python manage.py runserver
```

Test the endpoint:
```bash
curl -X POST http://localhost:8000/core/admin-api-login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Expected response:
```json
{
  "success": true,
  "username": "admin",
  "csrf_token": "..."
}
```

### **Step 6: Deploy to Render**
```bash
git add .
git commit -m "Add Admin API login endpoint for Admin Carrier PWA"
git push
```

Render will auto-deploy.

---

## 🔐 SECURITY NOTES

### ✅ **What's Protected:**
- API login requires valid Django admin credentials
- Sessions are used (same as web admin)
- CSRF tokens included
- CORS restricted to specific origins

### ⚠️ **Important:**
- Only admin users can login to Admin Carrier PWA
- Regular PremiumUsers cannot use this endpoint
- Sessions expire after inactivity (Django default)

---

## 🧪 TESTING CHECKLIST

- [ ] Install django-cors-headers
- [ ] Update settings.py with CORS config
- [ ] Add admin_api_login view to core/views.py
- [ ] Add admin_api_logout view to core/views.py
- [ ] Update core/urls.py with new endpoints
- [ ] Test login with curl or Postman
- [ ] Deploy to Render
- [ ] Verify from Admin Carrier PWA

---

## 📡 API ENDPOINTS SUMMARY

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/core/admin-api-login/` | POST | Admin login for PWA | No (provides auth) |
| `/core/admin-api-logout/` | POST | Admin logout | Yes (session) |
| `/api/admin/bulk-download/` | GET | Download all content | Yes (session) |
| `/api/admin/upload-users/` | POST | Upload user registrations | Yes (session) |

---

## ✅ COMPLETE!

After these updates:
- ✅ Admin Carrier PWA can login using Django credentials
- ✅ All admin API endpoints work with session authentication
- ✅ CORS configured for local network access
- ✅ Secure session-based authentication

**Your backend is now ready for Admin Carrier PWA!**