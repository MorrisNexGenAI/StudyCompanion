# ============================================================================
# FILE 1: scan/utils/ai.py - UPDATED WITH CLEAN FORMATTING + MODEL DETECTION
# ============================================================================

import os
import time
import requests
from django.conf import settings


class AIRefineError(Exception):
    """Custom exception for AI refine errors"""
    pass


# ==================================================
# API KEYS
# ==================================================

def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
    if not key:
        raise AIRefineError("GEMINI_API_KEY not found")
    return key


def get_groq_api_key():
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
    Priority: llama-3.3-70b-versatile > llama-3.1-70b-versatile > llama3-70b-8192 > first available
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
    
    # Ensure blank lines between sections (Answer, Explanation, Example)
    # Add blank line before Explanation if not present
    text = re.sub(r'([^\n])\n(Explanation:)', r'\1\n\n\2', text)
    
    # Add blank line before Example if not present
    text = re.sub(r'([^\n])\n(Example:)', r'\1\n\n\2', text)
    
    # Add blank line before --- separator if not present
    text = re.sub(r'([^\n])\n(---)', r'\1\n\n\2', text)
    
    return text


# ==================================================
# GEMINI REFINER
# ==================================================

def refine_with_gemini(
    raw_text: str,
    topic_title: str = "",
    max_retries: int = 8,
    base_delay: int = 5,
):
    """
    Uses Gemini to generate COMPLETE Q&A coverage.
    Returns clean, formatted text without markdown symbols.
    """

    api_key = get_gemini_api_key()
    start_time = time.time()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={api_key}"
    )

    prompt = f"""You are a study guide expert helping community college students in Liberia, West Africa. Convert these messy OCR-extracted student notes into comprehensive Q&A format.

Topic: {topic_title}

OCR TEXT:
{raw_text}

CRITICAL INSTRUCTIONS:
1. Analyze ALL the content in the OCR text thoroughly
2. Identify EVERY main concept, key term, process, definition, and important detail
3. Create a question for EACH significant piece of information
4. Generate AT LEAST 10-20 questions (more if the content is extensive)
5. Cover 100% of the important material - don't skip anything
6. Fix all OCR errors and typos
7. Organize questions in logical order

BREVITY REQUIREMENTS - VERY IMPORTANT:
- Keep ALL answers brief and concise (1-2 sentences maximum)
- Keep ALL explanations brief (1-2 sentences maximum)
- Keep ALL examples brief and specific (1-2 sentences maximum)
- EXCEPTION: If the answer is a table, list, or diagram, reproduce it fully and accurately
- For tables: Use markdown table format with proper alignment
- For lists: Present all items clearly
- Get straight to the point - no unnecessary words

EXAMPLE REQUIREMENTS - MANDATORY:
- EVERY question MUST have an example - no exceptions
- Make examples relevant to Liberia, West Africa, or local African context
- Use examples students in Liberia can relate to
- For health topics: use diseases/conditions common in West Africa (malaria, cholera, Ebola, typhoid)
- For business topics: use local Liberian businesses, markets (Waterside Market, Red Light Market), street vendors
- For criminal justice: use Liberian law enforcement, courts, or local examples
- For management: use local organizations, NGOs, or community groups
- For agriculture: cassava, rubber, rice farming
- Make examples practical and culturally appropriate

FORMATTING RULES - IMPORTANT:
- Use simple Q1:, Q2:, Q3: format (no ### symbols)
- Use "Answer:", "Explanation:", "Example:" (no ** bold markers)
- Leave blank lines between Answer, Explanation, and Example sections
- Keep structure clean and readable
- Separate Q&As with a line of dashes (---)
- For tables in answers: use proper markdown table format

FORMAT TEMPLATE (repeat for ALL concepts):

Q1: [First concept question]
Answer: [Brief, concise answer in 1-2 sentences OR full table/list if applicable]

Explanation: [Brief 1-2 sentence explanation of why this matters]

Example: [Brief 1-2 sentence example relevant to Liberia/West Africa - MANDATORY]

---

Q2: [Second concept question]
Answer: [Brief answer OR table/list if needed]

Explanation: [Brief explanation]

Example: [Brief local example - MANDATORY]

---

[Continue with Q3, Q4, Q5... until ALL content is covered]

CRITICAL REMINDERS:
- Be CONCISE - every answer, explanation, and example should be brief (1-2 sentences)
- Do NOT skip examples - every Q&A needs one
- Do NOT stop at 1-2 questions - cover everything
- EXCEPTION: Tables, lists, and diagrams should be complete and detailed
- Make examples locally relevant to West African/Liberian context

Begin now:"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
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
                time.sleep(delay)
                attempt += 1
                continue

            response.raise_for_status()
            data = response.json()

            refined_text = (
                data["candidates"][0]["content"]["parts"][0]["text"]
            )

            # Clean formatting
            refined_text = clean_markdown_formatting(refined_text)

            processing_time = time.time() - start_time
            qa_count = refined_text.count("Q") - refined_text.count("Q&A")  # Count Q1:, Q2:, etc.

            if qa_count < 2:
                raise AIRefineError(f"Gemini only generated {qa_count} question(s). Content may be too complex or API response incomplete.")

            return refined_text, processing_time, qa_count

        except requests.exceptions.RequestException as e:
            raise AIRefineError(f"Gemini request failed: {e}")

        except Exception as e:
            raise AIRefineError(f"Gemini refine error: {e}")


# ==================================================
# GROQ REFINER
# ==================================================

def refine_with_groq(
    raw_text: str,
    topic_title: str = "",
    max_retries: int = 5,
    base_delay: int = 3,
):
    """
    Uses Groq Llama to generate comprehensive Q&As.
    Auto-detects best available model.
    Returns clean formatted text.
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

    prompt = f"""You are a study guide creator helping students in Liberia, West Africa. Convert these messy OCR notes into comprehensive Q&A format.

Topic: {topic_title}

OCR TEXT:
{raw_text}

CRITICAL INSTRUCTIONS:
1. Read through ALL the content carefully
2. Identify EVERY main concept, term, process, and key detail
3. Create a question for EACH important piece of information
4. Generate 10-20+ questions depending on content length
5. Cover ALL the material - don't leave anything out
6. Fix OCR errors and organize logically

EXAMPLE REQUIREMENTS - MANDATORY:
- EVERY question MUST include an example - no exceptions
- Make examples relevant to Liberia, West Africa, or local African context
- Use examples that Liberian students can relate to
- Health topics: diseases/conditions common in West Africa (malaria, cholera, Ebola, typhoid)
- Business topics: local markets, petty trading, Monrovia businesses, street vendors
- Criminal justice: Liberian courts, police, local law enforcement
- Management: local NGOs, community organizations, market associations
- Agriculture: cassava farming, rubber plantations, local crops
- Make examples practical and culturally appropriate

FORMATTING RULES - IMPORTANT:
- Use simple Q1:, Q2:, Q3: format (no ### symbols)
- Use "Answer:", "Explanation:", "Example:" (no ** bold markers)
- Leave blank lines between Answer, Explanation, and Example sections
- Keep it clean and readable
- Separate Q&As with --- dashes

FORMAT (repeat for EVERY concept):

Q1: [Question about first concept]
Answer: [Concise answer]

Explanation: [Brief explanation of why this matters]

Example: [Quick practical example relevant to Liberia - MANDATORY]

---

Q2: [Question about second concept]
Answer: [Concise answer]

Explanation: [Brief explanation]

Example: [Another local example - MANDATORY]

---

[Continue Q3, Q4, Q5... until EVERYTHING is covered]

CRITICAL REMINDERS:
- Do NOT skip examples - every single Q&A needs one
- Do NOT stop at 1-2 questions - be thorough
- Make examples locally relevant to West African/Liberian context

Begin:"""

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
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
                time.sleep(delay)
                attempt += 1
                continue

            response.raise_for_status()
            data = response.json()

            refined_text = data["choices"][0]["message"]["content"]

            # Clean formatting
            refined_text = clean_markdown_formatting(refined_text)

            processing_time = time.time() - start_time
            qa_count = refined_text.count("Q") - refined_text.count("Q&A")

            if qa_count < 2:
                raise AIRefineError(f"Groq only generated {qa_count} question(s). Response may be incomplete.")

            return refined_text, processing_time, qa_count

        except requests.exceptions.RequestException as e:
            raise AIRefineError(f"Groq request failed: {e}")

        except Exception as e:
            raise AIRefineError(f"Groq refine error: {e}")


# ==================================================
# CONNECTION TESTS
# ==================================================

def test_gemini_connection():
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
