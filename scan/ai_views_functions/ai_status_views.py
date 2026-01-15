
# ==================== ai_views_functions/ai_status_views.py ====================
"""
AI Status views - Check AI service availability
"""
from django.http import JsonResponse

from ..utils.ai import test_gemini_connection, test_groq_connection


def ai_status(request):
    """Check if AI APIs are working"""
    gemini_ok, gemini_msg = test_gemini_connection()
    groq_ok, groq_msg = test_groq_connection()
    
    return JsonResponse({
        'gemini': {'ok': gemini_ok, 'message': gemini_msg},
        'groq': {'ok': groq_ok, 'message': groq_msg},
        'overall': gemini_ok or groq_ok
    })

