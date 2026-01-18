# ==================== core/views.py ====================
"""
Authentication views for backend admin users
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def admin_login(request):
    """Login page for backend administrators"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password')
            return render(request, 'core/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.display_name}!')
                
                # Redirect to 'next' parameter or home
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, 'Your account has been deactivated')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/login.html')


@login_required(login_url='admin_login')
def admin_logout(request):
    """Logout current user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('admin_login')


@login_required(login_url='admin_login')
def account_settings(request):
    """Account settings page - change password and update profile"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Change Password
        if action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not all([current_password, new_password, confirm_password]):
                messages.error(request, 'All password fields are required')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            elif len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters')
            elif not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('core:account_settings')
        
        # Update Profile
        elif action == 'update_profile':
            full_name = request.POST.get('full_name', '').strip()
            request.user.full_name = full_name
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:account_settings')
    
    return render(request, 'core/account_settings.html')


@login_required(login_url='admin_login')
def admin_password_reset(request):
    """
    Admin-only password reset page.
    For when you forget your password, you can reset it here
    using your username and a new password.
    """
    # Only superusers can access this
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can reset passwords')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not all([username, new_password, confirm_password]):
            messages.error(request, 'All fields are required')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
        elif len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, f'Password reset successful for {username}')
                return redirect('core:admin_password_reset')
            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found')
    
    # Get all users for the dropdown
    users = User.objects.filter(is_active=True).order_by('username')
    
    return render(request, 'core/admin_password_reset.html', {
        'users': users
    })

    