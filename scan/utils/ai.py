# ============================================================================
# FILE: scan/utils/ai.py - CLEAN VERSION WITH PROMPTS MODULE
# ============================================================================

import os
import time
import requests
from django.conf import settings
from .prompts import get_easy_prompt, get_medium_prompt, get_difficult_prompt


class AIRefineError(Exception):
    """Custom exception for AI refine errors"""
    pass


# ==================================================
# API KEYS
# ==================================================

def get_gemini_api_key():
    """Retrieve Gemini API key from environment or settings."""
    key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
    if not key:
        raise AIRefineError("GEMINI_API_KEY not found")
    return key


def get_groq_api_key():
    """Retrieve Groq API key from environment or settings."""
    key = os.environ.get("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
    if not key:
        raise AIRefineError("GROQ_API_KEY not found")
    return key


# ==================================================
# GROQ MODEL DETECTION
# ==================================================

def get_available_groq_models():
    """
    Fetches available Groq models dynamically.
    Returns list of model IDs or empty list on error.
    """
    try:
        api_key = get_groq_api_key()
        url = "https://api.groq.com/openai/v1/models"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        models = [model['id'] for model in data.get('data', [])]
        return models
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return []


def get_best_groq_model():
    """
    Returns the best available Groq model.
    Priority: llama-3.3-70b > llama-3.1-70b > llama3-70b > mixtral-8x7b
    """
    available_models = get_available_groq_models()
    
    if not available_models:
        return "llama-3.1-70b-versatile"  # Fallback
    
    # Priority list
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
    ]
    
    # Return first match
    for preferred in preferred_models:
        if preferred in available_models:
            return preferred
    
    # Return first available if no match
    return available_models[0]


# ==================================================
# TEXT FORMATTING CLEANER
# ==================================================

def clean_markdown_formatting(text):
    """
    Removes markdown symbols and ensures proper spacing.
    - Removes ### from headings
    - Removes ** from bold text
    - Adds blank lines between Answer, Explanation, and Example
    - Keeps structure readable
    """
    import re
    
    # Remove ### from Q headers but keep Q number
    text = re.sub(r'###\s+Q(\d+):', r'Q\1:', text)
    
    # Remove ** from Answer:, Explanation:, Example:
    text = re.sub(r'\*\*Answer:\*\*', 'Answer:', text)
    text = re.sub(r'\*\*Explanation:\*\*', 'Explanation:', text)
    text = re.sub(r'\*\*Example:\*\*', 'Example:', text)
    
    # Remove any remaining ** bold markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Ensure blank lines between sections
    text = re.sub(r'([^\n])\n(Explanation:)', r'\1\n\n\2', text)
    text = re.sub(r'([^\n])\n(Example:)', r'\1\n\n\2', text)
    text = re.sub(r'([^\n])\n(---)', r'\1\n\n\2', text)
    
    return text


# ==================================================
# GEMINI REFINER
# ==================================================

def refine_with_gemini(
    raw_text: str,
    topic_title: str = "",
    difficulty_level: str = "medium",
    max_retries: int = 8,
    base_delay: int = 5,
):
    """
    Uses Gemini to generate Q&A based on difficulty level.
    
    Args:
        raw_text: Raw OCR text to process
        topic_title: Title of the topic
        difficulty_level: 'easy', 'medium', or 'difficult'
        max_retries: Maximum retry attempts for rate limiting
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        tuple: (refined_text, processing_time, qa_count)
    
    Raises:
        AIRefineError: If generation fails
    """

    api_key = get_gemini_api_key()
    start_time = time.time()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={api_key}"
    )

    # SELECT PROMPT BASED ON DIFFICULTY
    if difficulty_level == 'easy':
        prompt = get_easy_prompt(topic_title, raw_text)
    elif difficulty_level == 'difficult':
        prompt = get_difficult_prompt(topic_title, raw_text)
    else:  # medium (default)
        prompt = get_medium_prompt(topic_title, raw_text)

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8000,
            "topP": 0.95,
            "topK": 40
        }
    }

    attempt = 0

    while True:
        try:
            response = requests.post(url, json=payload, timeout=120)

            if response.status_code == 429:
                if attempt >= max_retries:
                    raise AIRefineError("Gemini rate-limited too many times")
                
                delay = base_delay * (2 ** attempt)
                print(f"Rate limited. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                attempt += 1
                continue

            response.raise_for_status()
            data = response.json()

            refined_text = data["candidates"][0]["content"]["parts"][0]["text"]
            refined_text = clean_markdown_formatting(refined_text)

            processing_time = time.time() - start_time
            qa_count = refined_text.count("Q") - refined_text.count("Q&A")

            if qa_count < 2:
                raise AIRefineError(f"Gemini only generated {qa_count} question(s). Content may be too complex.")

            return refined_text, processing_time, qa_count

        except requests.exceptions.RequestException as e:
            raise AIRefineError(f"Gemini request failed: {e}")
        except KeyError as e:
            raise AIRefineError(f"Unexpected Gemini response format: {e}")
        except Exception as e:
            raise AIRefineError(f"Gemini refine error: {e}")


# ==================================================
# GROQ REFINER
# ==================================================

def refine_with_groq(
    raw_text: str,
    topic_title: str = "",
    difficulty_level: str = "medium",
    max_retries: int = 5,
    base_delay: int = 3,
):
    """
    Uses Groq Llama to generate Q&A based on difficulty level.
    Auto-detects best available model.
    
    Args:
        raw_text: Raw OCR text to process
        topic_title: Title of the topic
        difficulty_level: 'easy', 'medium', or 'difficult'
        max_retries: Maximum retry attempts for rate limiting
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        tuple: (refined_text, processing_time, qa_count)
    
    Raises:
        AIRefineError: If generation fails
    """

    api_key = get_groq_api_key()
    start_time = time.time()

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Get best available model
    model = get_best_groq_model()

    # SELECT PROMPT BASED ON DIFFICULTY
    if difficulty_level == 'easy':
        prompt = get_easy_prompt(topic_title, raw_text)
    elif difficulty_level == 'difficult':
        prompt = get_difficult_prompt(topic_title, raw_text)
    else:  # medium (default)
        prompt = get_medium_prompt(topic_title, raw_text)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 6000,
        "top_p": 0.95,
    }

    attempt = 0

    while True:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=90)

            if response.status_code == 429:
                if attempt >= max_retries:
                    raise AIRefineError("Groq rate-limited too many times")
                
                delay = base_delay * (2 ** attempt)
                print(f"Rate limited. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                attempt += 1
                continue

            response.raise_for_status()
            data = response.json()

            refined_text = data["choices"][0]["message"]["content"]
            refined_text = clean_markdown_formatting(refined_text)

            processing_time = time.time() - start_time
            qa_count = refined_text.count("Q") - refined_text.count("Q&A")

            if qa_count < 2:
                raise AIRefineError(f"Groq only generated {qa_count} question(s). Response may be incomplete.")

            return refined_text, processing_time, qa_count

        except requests.exceptions.RequestException as e:
            raise AIRefineError(f"Groq request failed: {e}")
        except KeyError as e:
            raise AIRefineError(f"Unexpected Groq response format: {e}")
        except Exception as e:
            raise AIRefineError(f"Groq refine error: {e}")


# ==================================================
# CONNECTION TESTS
# ==================================================

def test_gemini_connection():
    """Test Gemini API connection."""
    try:
        api_key = get_gemini_api_key()
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-2.5-flash:generateContent"
            f"?key={api_key}"
        )
        
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": "Reply OK"}]}
            ]
        }
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return True, "Gemini connection successful"
    
    except Exception as e:
        return False, f"Gemini error: {e}"


def test_groq_connection():
    """Test Groq API connection."""
    try:
        api_key = get_groq_api_key()
        model = get_best_groq_model()
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Reply OK"}],
            "max_tokens": 10,
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return True, f"Groq connection successful (using {model})"
    
    except Exception as e:
        return False, f"Groq error: {e}"