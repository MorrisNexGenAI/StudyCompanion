# scan/utils/ocr.py
import requests
from django.conf import settings

# Your Colab OCR Engine URL (from ngrok)
COLAB_OCR_URL = getattr(settings, 'COLAB_OCR_URL', None)

def extract_text_from_image(image_path):
    """
    Extract text by calling Colab OCR Engine API (single image)
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


def extract_text_from_images_batch(image_paths):
    """
    Extract text from multiple images using batch processing (FASTER)
    
    Args:
        image_paths: List of image file paths
        
    Returns:
        List of dicts with format:
        [
            {'page': 1, 'text': '...', 'engine': 'EasyOCR', 'confidence': 85.5},
            {'page': 2, 'text': '...', 'engine': 'Tesseract', 'confidence': 88.0},
            ...
        ]
    """
    if not COLAB_OCR_URL:
        return [{"page": i+1, "text": "[Error: COLAB_OCR_URL not configured]", "engine": "error", "confidence": 0} 
                for i in range(len(image_paths))]
    
    try:
        # Open all images and prepare for batch upload
        files = {}
        file_handles = []
        
        for idx, img_path in enumerate(image_paths):
            f = open(img_path, 'rb')
            file_handles.append(f)
            files[f'file{idx+1}'] = f
        
        try:
            # Call batch API endpoint
            response = requests.post(
                f"{COLAB_OCR_URL}/extract-text-batch",
                files=files,
                timeout=120  # 2 minutes for batch
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    results = []
                    for idx, item in enumerate(result.get('results', []), 1):
                        text = item.get('text', '')
                        engine = item.get('engine_used', 'unknown')
                        confidence = item.get('confidence', 0)
                        
                        # Add metadata
                        metadata = f"[OCR Engine: {engine} | Confidence: {confidence:.1f}%]\n\n"
                        
                        results.append({
                            'page': idx,
                            'text': metadata + text if text else "[No text detected]",
                            'engine': engine,
                            'confidence': confidence
                        })
                    
                    return results
                else:
                    # Batch failed, return error for all
                    return [{"page": i+1, "text": "[Batch OCR processing failed]", "engine": "error", "confidence": 0} 
                            for i in range(len(image_paths))]
            else:
                return [{"page": i+1, "text": f"[OCR API Error {response.status_code}]", "engine": "error", "confidence": 0} 
                        for i in range(len(image_paths))]
        
        finally:
            # Close all file handles
            for f in file_handles:
                f.close()
                
    except requests.exceptions.Timeout:
        return [{"page": i+1, "text": "[OCR timeout - batch too large or connection slow]", "engine": "error", "confidence": 0} 
                for i in range(len(image_paths))]
    except requests.exceptions.ConnectionError:
        return [{"page": i+1, "text": "[Cannot connect to OCR engine - is Colab running?]", "engine": "error", "confidence": 0} 
                for i in range(len(image_paths))]
    except Exception as e:
        return [{"page": i+1, "text": f"[OCR Error: {str(e)}]", "engine": "error", "confidence": 0} 
                for i in range(len(image_paths))]


def test_ocr_connection():
    """Test if OCR engine is reachable"""
    if not COLAB_OCR_URL:
        return False, "COLAB_OCR_URL not configured"
    
    try:
        response = requests.get(f"{COLAB_OCR_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            batch_support = data.get('batch_support', False)
            gpu = data.get('gpu_available', 'unknown')
            
            status = f"OCR Engine healthy"
            if batch_support:
                status += " (Batch processing enabled)"
            
            return True, status
        return False, f"Health check failed: {response.status_code}"
    except Exception as e:
        return False, f"Cannot reach OCR engine: {str(e)}"