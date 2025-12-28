# ============================================================================
# FILE: scan/utils/ai.py - UPDATED WITH STRICT WORD COUNT ENFORCEMENT
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
# GEMINI REFINER - WITH STRICT WORD COUNT ENFORCEMENT
# ==================================================

def refine_with_gemini(
    raw_text: str,
    topic_title: str = "",
    max_retries: int = 8,
    base_delay: int = 5,
):
    """
    Uses Gemini to generate Q&A with STRICT word count limits.
    Returns clean, formatted text without markdown symbols.
    """

    api_key = get_gemini_api_key()
    start_time = time.time()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={api_key}"
    )

    prompt = f"""You are creating study flashcards for community college students in Monrovia, Liberia, West Africa.

Your ONLY job is to follow the EXACT format below. No creativity with formatting. No extra words.

Topic: {topic_title}

OCR TEXT:
{raw_text}

═══════════════════════════════════════════════════════════════════
ABSOLUTE WORD LIMITS - COUNT EVERY SINGLE WORD
═══════════════════════════════════════════════════════════════════

Answer: 4-6 words MAXIMUM (count: 1, 2, 3, 4, 5, 6 - STOP)
Explanation: 6-8 words MAXIMUM (count: 1, 2, 3, 4, 5, 6, 7, 8 - STOP)
Example: 5-7 words MAXIMUM (count: 1, 2, 3, 4, 5, 6, 7 - STOP)

FORBIDDEN:
❌ No "because...which...that" chains
❌ No repeating the question in the answer
❌ No compound sentences (no semicolons)
❌ No abstract examples (must be concrete)
❌ Commas only when grammatically necessary
❌ One sentence per field (Answer, Explanation, Example)

WORD COUNT ENFORCEMENT:
✓ If Answer exceeds 6 words → concept is too broad → SPLIT into 2 questions
✓ If Explanation exceeds 8 words → remove unnecessary words
✓ If Example exceeds 7 words → make it more specific

EXCEPTION - TABLES/LISTS:
- If the answer IS a table or list → reproduce it fully
- NO Explanation field (delete it)
- NO Example field (delete it)
- Only: Q + Answer (table/list) + separator

═══════════════════════════════════════════════════════════════════
PERFECT EXAMPLES - COPY THIS EXACT PATTERN
═══════════════════════════════════════════════════════════════════

EXAMPLE 1 - Health (West Africa Context):

Q1: What causes malaria transmission?
Answer: Infected female Anopheles mosquito bite

Explanation: Parasite enters bloodstream and infects red cells

Example: Monrovia rainy season increases mosquito breeding

---

EXAMPLE 2 - Business (Liberia Context):

Q2: What is petty trading?
Answer: Selling small goods for quick profit

Explanation: Low investment generates daily income for survival

Example: Waterside Market women sell rice cups

---

EXAMPLE 3 - Criminal Justice (Liberia Context):

Q3: What is due process?
Answer: Fair legal procedures protect accused rights

Explanation: Courts must follow rules before convicting anyone

Example: Monrovia Magistrate Court requires lawyer access

---

EXAMPLE 4 - Management (West Africa Context):

Q4: What is delegation?
Answer: Manager assigns tasks to team members

Explanation: Spreads workload and develops employee skills

Example: NGO supervisor assigns community health workers

---

EXAMPLE 5 - Agriculture (Liberia Context):

Q5: What is crop rotation?
Answer: Planting different crops each season

Explanation: Prevents soil depletion and reduces pest buildup

Example: Cassava then rice prevents soil exhaustion

---

EXAMPLE 6 - Education (West Africa Context):

Q6: What is formative assessment?
Answer: Ongoing checks during learning process

Explanation: Teachers adjust instruction based on student progress

Example: WASSCE mock exams identify weak areas

---

EXAMPLE 7 - Table Answer (NO Explanation/Example):

Q7: What are the three types of rocks?
Answer:
| Rock Type | Formation | Example |
|-----------|-----------|---------|
| Igneous | Cooled magma | Granite |
| Sedimentary | Compressed layers | Limestone |
| Metamorphic | Heat and pressure | Marble |

---

═══════════════════════════════════════════════════════════════════
LOCAL CONTEXT BANK - USE THESE IN EXAMPLES
═══════════════════════════════════════════════════════════════════

HEALTH:
- Diseases: malaria, cholera, Ebola, typhoid, yellow fever, HIV/AIDS
- Places: JFK Hospital, ELWA Hospital, Redemption Hospital, Phebe Hospital
- Context: rainy season, mosquito nets, oral rehydration, community health workers

BUSINESS:
- Markets: Waterside Market, Red Light Market, Duala Market, Soul Clinic
- Activities: petty trading, mobile money (Orange Money, MTN), street vending, market associations
- Context: daily sales, credit systems, market queens, transport unions

CRIMINAL JUSTICE:
- Institutions: Monrovia Magistrate Court, Temple of Justice, Liberian National Police (LNP)
- Context: bail hearings, magistrates, court clerks, police stations, customary law

MANAGEMENT:
- Organizations: local NGOs, community-based organizations (CBOs), market associations, UNMIL legacy programs
- Context: team leaders, supervisors, community health workers, volunteers

AGRICULTURE:
- Crops: cassava, rubber, rice, palm oil, cocoa, coffee, cocoyam
- Context: slash-and-burn, rainy season planting, rubber tappers, rice paddies, cooperative farming

EDUCATION:
- Institutions: University of Liberia, community colleges, Tubman University, WAEC
- Context: WASSCE exams, tuition fees, scholarship programs, peer tutoring, continuing education

GEOGRAPHY (Liberia):
- Places: Montserrado County, Bong County, Nimba County, Monrovia, Bushrod Island, Congo Town, Paynesville
- Context: coastal plains, tropical climate, rivers, Atlantic coast

GEOGRAPHY (West Africa):
- Countries: Sierra Leone, Guinea, Côte d'Ivoire, Ghana, Nigeria, Senegal
- Context: ECOWAS, shared borders, regional trade, Harmattan winds

═══════════════════════════════════════════════════════════════════
YOUR TASK - FOLLOW THIS EXACTLY
═══════════════════════════════════════════════════════════════════

1. Read ALL the OCR text carefully
2. Identify EVERY key concept, term, process, definition
3. Create 15-20 questions (cover everything important)
4. For EACH question:
   • Write Question clearly
   • Write Answer (4-6 words - COUNT THEM)
   • Write Explanation (6-8 words - COUNT THEM)
   • Write Example using LOCAL CONTEXT (5-7 words - COUNT THEM)
   • Add separator (---)

5. EXCEPTION: If answer is a table/list:
   • Write Question
   • Write Answer (full table/list)
   • NO Explanation
   • NO Example
   • Add separator (---)

6. Fix all OCR errors and typos
7. Organize questions in logical order

FORMAT TO COPY:

Q1: [Clear question about first concept]
Answer: [4-6 words maximum]

Explanation: [6-8 words maximum]

Example: [5-7 words using Liberia/West Africa context]

---

Q2: [Clear question about second concept]
Answer: [4-6 words maximum]

Explanation: [6-8 words maximum]

Example: [5-7 words using local context]

---

[Continue Q3, Q4, Q5... until ALL content covered]

CRITICAL REMINDERS:
✓ COUNT EVERY WORD - do not exceed limits
✓ EVERY question needs an example (unless table/list answer)
✓ Use LOCAL Liberian/West African context in examples
✓ Cover ALL important material from OCR text
✓ If concept is too broad for word limits → SPLIT into 2 questions
✓ Keep formatting clean (no ### or ** symbols)

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
# GROQ REFINER - WITH STRICT WORD COUNT ENFORCEMENT
# ==================================================

def refine_with_groq(
    raw_text: str,
    topic_title: str = "",
    max_retries: int = 5,
    base_delay: int = 3,
):
    """
    Uses Groq Llama to generate Q&A with STRICT word count limits.
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

    prompt = f"""You are creating study flashcards for students in Liberia, West Africa.

Follow the EXACT format below. No extra words. Count every word carefully.

Topic: {topic_title}

OCR TEXT:
{raw_text}

═══════════════════════════════════════════════════════════════════
WORD LIMITS - COUNT EACH WORD
═══════════════════════════════════════════════════════════════════

Answer: 4-6 words MAX
Explanation: 6-8 words MAX
Example: 5-7 words MAX

RULES:
❌ No "because/which/that" chains
❌ No repeating question in answer
❌ One sentence per field
❌ Commas only when necessary
✓ If Answer > 6 words → SPLIT into 2 questions

EXCEPTION: If answer is table/list → NO Explanation, NO Example

═══════════════════════════════════════════════════════════════════
PERFECT EXAMPLES - COPY THIS PATTERN
═══════════════════════════════════════════════════════════════════

Q1: What causes malaria transmission?
Answer: Infected female Anopheles mosquito bite

Explanation: Parasite enters bloodstream and infects red cells

Example: Monrovia rainy season increases mosquito breeding

---

Q2: What is petty trading?
Answer: Selling small goods for quick profit

Explanation: Low investment generates daily income for survival

Example: Waterside Market women sell rice cups

---

Q3: What is due process?
Answer: Fair legal procedures protect accused rights

Explanation: Courts must follow rules before convicting anyone

Example: Monrovia Magistrate Court requires lawyer access

---

Q4: What is formative assessment?
Answer: Ongoing checks during learning process

Explanation: Teachers adjust instruction based on student progress

Example: WASSCE mock exams identify weak areas

---

Q5: What is crop rotation?
Answer: Planting different crops each season

Explanation: Prevents soil depletion and reduces pest buildup

Example: Cassava then rice prevents soil exhaustion

---

═══════════════════════════════════════════════════════════════════
LOCAL CONTEXT - USE IN EXAMPLES
═══════════════════════════════════════════════════════════════════

Health: malaria, cholera, Ebola, JFK Hospital, ELWA Hospital, community health workers
Business: Waterside Market, Red Light Market, petty trading, mobile money, market queens
Justice: Monrovia Magistrate Court, Temple of Justice, Liberian National Police
Management: local NGOs, CBOs, market associations, UNMIL programs
Agriculture: cassava, rubber, rice paddies, palm oil, slash-and-burn
Education: University of Liberia, WASSCE exams, Tubman University, peer tutoring
Geography: Montserrado County, Monrovia, West Africa (ECOWAS, Ghana, Nigeria, Sierra Leone)

═══════════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════════

1. Read ALL OCR text
2. Identify EVERY key concept
3. Create 15-20 questions
4. For EACH question:
   • Question (clear)
   • Answer (4-6 words - COUNT)
   • Explanation (6-8 words - COUNT)
   • Example (5-7 words - LOCAL context)
   • Separator (---)

5. EXCEPTION for tables/lists:
   • Question + Answer (full table) + Separator
   • NO Explanation, NO Example

FORMAT:

Q1: [Question]
Answer: [4-6 words]

Explanation: [6-8 words]

Example: [5-7 words - Liberia/West Africa]

---

Q2: [Question]
Answer: [4-6 words]

Explanation: [6-8 words]

Example: [5-7 words - local context]

---

[Continue until ALL content covered]

REMINDERS:
✓ COUNT words - never exceed limits
✓ Use Liberian/West African examples
✓ Cover ALL important material
✓ Split broad concepts into multiple questions

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
