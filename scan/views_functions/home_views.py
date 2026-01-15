# ==================== views_functions/home_views.py ====================
"""
Home view - Main landing page
"""
from django.shortcuts import render


def home(request):
    """Main landing page with two options"""
    return render(request, 'scan/partials/home.html')

