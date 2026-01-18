# ==================== views_functions/home_views.py ====================
"""
Home view - Main landing page
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='core:admin_login')
def home(request):
    """Main landing page with two options"""
    return render(request, 'scan/partials/home.html')