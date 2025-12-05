import requests
import time

HF_TOKEN = "YOUR_HF_TOKEN_HERE"

def generate_summary_and_questions(text, retry_count=0):
    """
    Use facebook/bart-large-cnn for summarization (more reliable)
    Then use separate model for questions
    """
    
    if not text or len(text) < 50:
        return "⚠️ Not enough text extracted. Please retake photos with better lighting and ensure text is clear."
    
    # Limit text
    text = text[:8000]
    
    try:
        # STEP 1: Generate summary
        summary = generate_summary(text)
        
        # STEP 2: Generate questions
        questions = generate_questions(text)
        
        # Combine results
        result = f"""SUMMARY:
{summary}

KEY POINTS:
{extract_key_points(text)}

PRACTICE QUESTIONS:
{questions}
"""
        return result
        
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}\n\nExtracted Text:\n{text[:500]}...\n\nPlease copy this text and use ChatGPT manually."

def generate_summary(text):
    """Generate summary using BART"""
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": text[:1000],  # BART has token limit
        "parameters": {
            "max_length": 150,
            "min_length": 50
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("summary_text", "Summary generation failed")
        return "Could not generate summary"
    except:
        return "Summary generation failed"

def generate_questions(text):
    """Generate questions (simplified)"""
    # For now, return template questions
    # Later you can use a QG model if needed
    return """1. What is the main topic discussed in these notes?
2. Explain the key concepts mentioned.
3. What are the most important points to remember?
4. How would you apply this information?
5. What questions would you ask to test understanding of this material?
6. Summarize the main ideas in your own words.
7. What connections can you make to other topics?
8. What examples illustrate these concepts?"""

def extract_key_points(text):
    """Extract key points using simple heuristics"""
    lines = text.split('\n')
    key_points = []
    
    for line in lines:
        line = line.strip()
        # Look for lines that might be headings or important
        if len(line) > 20 and len(line) < 150:
            if any(char.isupper() for char in line[:10]):  # Starts with capitals
                key_points.append(f"• {line}")
        
        if len(key_points) >= 7:
            break
    
    if len(key_points) < 3:
        # Fallback: just take first few substantial lines
        for line in lines:
            if len(line) > 30:
                key_points.append(f"• {line[:100]}")
            if len(key_points) >= 5:
                break
    
    return '\n'.join(key_points) if key_points else "• Review all content in the notes\n• Focus on main concepts\n• Practice key definitions"