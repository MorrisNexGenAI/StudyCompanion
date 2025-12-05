import requests
from django.conf import settings

# Your Colab OCR Engine URL (from ngrok)
COLAB_OCR_URL = getattr(settings, 'COLAB_OCR_URL', None)

def extract_text_from_image(image_path):
    """
    Extract text by calling Colab OCR Engine API
    """
    if not COLAB_OCR_URL:
        return "[Error: COLAB_OCR_URL not configured in settings]"
    
    try:
        # Open image file
        with open(image_path, 'rb') as f:
            files = {'file': f}
            
            # Call Colab API
            response = requests.post(
                f"{COLAB_OCR_URL}/extract-text",
                files=files,
                timeout=60  # 60 seconds timeout
            )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                text = result.get('text', '')
                engine = result.get('engine_used', 'unknown')
                confidence = result.get('confidence', 0)
                
                # Add metadata comment at top
                metadata = f"[OCR Engine: {engine} | Confidence: {confidence:.1f}%]\n\n"
                
                return metadata + text if text else "[No text detected]"
            else:
                return "[OCR processing failed]"
        else:
            return f"[OCR API Error {response.status_code}]"
            
    except requests.exceptions.Timeout:
        return "[OCR timeout - image might be too large or connection slow]"
    except requests.exceptions.ConnectionError:
        return "[Cannot connect to OCR engine - is Colab running?]"
    except Exception as e:
        return f"[OCR Error: {str(e)}]"

def test_ocr_connection():
    """Test if OCR engine is reachable"""
    if not COLAB_OCR_URL:
        return False, "COLAB_OCR_URL not configured"
    
    try:
        response = requests.get(f"{COLAB_OCR_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"OCR Engine healthy (GPU: {data.get('gpu_available', False)})"
        return False, f"Health check failed: {response.status_code}"
    except Exception as e:
        return False, f"Cannot reach OCR engine: {str(e)}"