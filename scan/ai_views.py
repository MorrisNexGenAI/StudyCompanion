
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Topic, AIRefine
from .utils.ai import (
    refine_with_gemini, 
    refine_with_groq, 
    test_gemini_connection, 
    test_groq_connection,
    AIRefineError
)


def ai_refine_page(request, topic_id):
    """
    Show AI Refine comparison page with all three versions
    """
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Get existing AI refines
    gemini_refine = AIRefine.objects.filter(topic=topic, provider='gemini').first()
    groq_refine = AIRefine.objects.filter(topic=topic, provider='groq').first()
    
    context = {
        'topic': topic,
        'gemini_refine': gemini_refine,
        'groq_refine': groq_refine,
    }
    
    return render(request, 'scan/partials/ai_refine.html', context)


@csrf_exempt
def generate_ai_refine(request, topic_id):
    """
    Generate AI refines - SELECTIVE: gemini, groq, or both
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    topic = get_object_or_404(Topic, id=topic_id)
    provider = request.POST.get('provider', 'both')  # 'gemini', 'groq', or 'both'
    
    results = {}
    
    # Generate Gemini refine
    if provider in ['gemini', 'both']:
        try:
            gemini_refine, _ = AIRefine.objects.get_or_create(
                topic=topic,
                provider='gemini',
                defaults={'status': 'processing'}
            )
            
            # Check if already exists and ask for confirmation
            if gemini_refine.status == 'completed' and gemini_refine.refined_text:
                # Regenerate anyway (user clicked button)
                pass
            
            gemini_refine.status = 'processing'
            gemini_refine.save()
            
            refined_text, proc_time, qa_count = refine_with_gemini(
                topic.raw_text, 
                topic.title
            )
            
            gemini_refine.refined_text = refined_text
            gemini_refine.processing_time = proc_time
            gemini_refine.qa_count = qa_count
            gemini_refine.status = 'completed'
            gemini_refine.error_message = ''
            gemini_refine.save()
            
            results['gemini'] = {
                'success': True,
                'qa_count': qa_count,
                'processing_time': round(proc_time, 2),
                'preview': refined_text[:300] + '...' if len(refined_text) > 300 else refined_text
            }
            
        except AIRefineError as e:
            gemini_refine.status = 'failed'
            gemini_refine.error_message = str(e)
            gemini_refine.save()
            results['gemini'] = {'success': False, 'error': str(e)}
    
    # Generate Groq refine
    if provider in ['groq', 'both']:
        try:
            groq_refine, _ = AIRefine.objects.get_or_create(
                topic=topic,
                provider='groq',
                defaults={'status': 'processing'}
            )
            
            groq_refine.status = 'processing'
            groq_refine.save()
            
            refined_text, proc_time, qa_count = refine_with_groq(
                topic.raw_text,
                topic.title
            )
            
            groq_refine.refined_text = refined_text
            groq_refine.processing_time = proc_time
            groq_refine.qa_count = qa_count
            groq_refine.status = 'completed'
            groq_refine.error_message = ''
            groq_refine.save()
            
            results['groq'] = {
                'success': True,
                'qa_count': qa_count,
                'processing_time': round(proc_time, 2),
                'preview': refined_text[:300] + '...' if len(refined_text) > 300 else refined_text
            }
            
        except AIRefineError as e:
            groq_refine.status = 'failed'
            groq_refine.error_message = str(e)
            groq_refine.save()
            results['groq'] = {'success': False, 'error': str(e)}
    
    return JsonResponse(results)


@csrf_exempt
def select_ai_refine(request, topic_id):
    """
    User selects which AI refine to use (or keeps manual)
    """
    if request.method != 'POST':
        return redirect('ai_refine_page', topic_id=topic_id)
    
    topic = get_object_or_404(Topic, id=topic_id)
    selection = request.POST.get('selection')
    
    if selection == 'gemini':
        gemini_refine = get_object_or_404(AIRefine, topic=topic, provider='gemini')
        topic.refined_summary = gemini_refine.refined_text
        topic.save()
        message = '✓ Gemini refine saved to topic!'
        
    elif selection == 'groq':
        groq_refine = get_object_or_404(AIRefine, topic=topic, provider='groq')
        topic.refined_summary = groq_refine.refined_text
        topic.save()
        message = '✓ Groq refine saved to topic!'
        
    elif selection == 'manual':
        message = '✓ Keeping manual refined summary'
    
    else:
        return JsonResponse({'error': 'Invalid selection'}, status=400)
    
    return render(request, 'scan/partials/ai_select_success.html', {
        'topic': topic,
        'message': message,
        'selection': selection
    })


def ai_status(request):
    """Check if AI APIs are working"""
    gemini_ok, gemini_msg = test_gemini_connection()
    groq_ok, groq_msg = test_groq_connection()
    
    return JsonResponse({
        'gemini': {'ok': gemini_ok, 'message': gemini_msg},
        'groq': {'ok': groq_ok, 'message': groq_msg},
        'overall': gemini_ok or groq_ok
    })
