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
    """Show AI Refine comparison page"""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Get difficulty from query parameter or use topic's stored difficulty
    difficulty = request.GET.get('difficulty', topic.difficulty_level or 'medium')
    
    # Get AI refines for the SELECTED difficulty (not just topic's stored one)
    gemini_refine = AIRefine.objects.filter(
        topic=topic, 
        provider='gemini',
        difficulty_level=difficulty
    ).order_by('-created_at').first()  # Get latest for this difficulty
    
    groq_refine = AIRefine.objects.filter(
        topic=topic, 
        provider='groq',
        difficulty_level=difficulty
    ).order_by('-created_at').first()  # Get latest for this difficulty
    
    context = {
        'topic': topic,
        'gemini_refine': gemini_refine,
        'groq_refine': groq_refine,
        'difficulty': difficulty,  # Pass the selected difficulty to template
    }
    
    return render(request, 'scan/partials/ai_refine.html', context)


@csrf_exempt
def generate_ai_refine(request, topic_id):
    """Generate AI refines with user-selected difficulty level"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    topic = get_object_or_404(Topic, id=topic_id)
    provider = request.POST.get('provider', 'both')
    
    # GET DIFFICULTY FROM POST REQUEST (sent from JavaScript)
    difficulty = request.POST.get('difficulty', 'medium')
    
    # OPTIONAL: Update topic's stored difficulty level
    # Uncomment these lines if you want to save the user's choice:
    topic.difficulty_level = difficulty
    topic.save(update_fields=['difficulty_level', 'updated_at'])
    
    results = {}
    
    # Generate Gemini refine
    if provider in ['gemini', 'both']:
        try:
            # Get or create with the SELECTED difficulty
            gemini_refine, _ = AIRefine.objects.get_or_create(
                topic=topic,
                provider='gemini',
                difficulty_level=difficulty,  # Use selected difficulty
                defaults={'status': 'processing'}
            )
            
            gemini_refine.status = 'processing'
            gemini_refine.save()
            
            refined_text, proc_time, qa_count = refine_with_gemini(
                topic.raw_text, 
                topic.title,
                difficulty_level=difficulty  # Pass selected difficulty to AI
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
                'difficulty': difficulty,
                'preview': refined_text[:300] + '...' if len(refined_text) > 300 else refined_text
            }
            
        except AIRefineError as e:
            if 'gemini_refine' in locals():
                gemini_refine.status = 'failed'
                gemini_refine.error_message = str(e)
                gemini_refine.save()
            results['gemini'] = {'success': False, 'error': str(e)}
    
    # Generate Groq refine
    if provider in ['groq', 'both']:
        try:
            # Get or create with the SELECTED difficulty
            groq_refine, _ = AIRefine.objects.get_or_create(
                topic=topic,
                provider='groq',
                difficulty_level=difficulty,  # Use selected difficulty
                defaults={'status': 'processing'}
            )
            
            groq_refine.status = 'processing'
            groq_refine.save()
            
            refined_text, proc_time, qa_count = refine_with_groq(
                topic.raw_text,
                topic.title,
                difficulty_level=difficulty  # Pass selected difficulty to AI
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
                'difficulty': difficulty,
                'preview': refined_text[:300] + '...' if len(refined_text) > 300 else refined_text
            }
            
        except AIRefineError as e:
            if 'groq_refine' in locals():
                groq_refine.status = 'failed'
                groq_refine.error_message = str(e)
                groq_refine.save()
            results['groq'] = {'success': False, 'error': str(e)}
    
    return JsonResponse(results)


@csrf_exempt
def select_ai_refine(request, topic_id):
    """User selects which AI refine to use"""
    if request.method != 'POST':
        return redirect('ai_refine_page', topic_id=topic_id)
    
    topic = get_object_or_404(Topic, id=topic_id)
    selection = request.POST.get('selection')
    
    # Get the difficulty from the AI refine being selected
    # This ensures we save the refine that was actually generated
    difficulty = None
    
    if selection == 'gemini':
        gemini_refine = AIRefine.objects.filter(
            topic=topic, 
            provider='gemini',
            status='completed'
        ).order_by('-created_at').first()
        
        if gemini_refine:
            topic.refined_summary = gemini_refine.refined_text
            difficulty = gemini_refine.difficulty_level
            # Update topic's difficulty to match the selected refine
            topic.difficulty_level = difficulty
            topic.save()
            message = f'✓ Gemini refine ({difficulty} level) saved to topic!'
        else:
            return JsonResponse({'error': 'No Gemini refine found'}, status=400)
        
    elif selection == 'groq':
        groq_refine = AIRefine.objects.filter(
            topic=topic, 
            provider='groq',
            status='completed'
        ).order_by('-created_at').first()
        
        if groq_refine:
            topic.refined_summary = groq_refine.refined_text
            difficulty = groq_refine.difficulty_level
            # Update topic's difficulty to match the selected refine
            topic.difficulty_level = difficulty
            topic.save()
            message = f'✓ Groq refine ({difficulty} level) saved to topic!'
        else:
            return JsonResponse({'error': 'No Groq refine found'}, status=400)
        
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
