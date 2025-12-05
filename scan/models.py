from django.db import models
from core.models import BaseModel

class Course(BaseModel):
    """Represents a course (e.g., BIO 202, CHEM 101)"""
    name = models.CharField(max_length=200)  # e.g., "BIO 202"
    subject = models.CharField(max_length=200, blank=True)  # e.g., "Cell Biology"
    year = models.CharField(max_length=20, blank=True)  # e.g., "2024"
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.subject}" if self.subject else self.name
    
    def get_total_topics(self):
        return self.topics.count()
    
    def get_refined_count(self):
        return self.topics.filter(refined_summary__isnull=False).exclude(refined_summary='').count()
    
    def get_full_refined_text(self):
        """Combine all refined summaries in order"""
        topics = self.topics.filter(refined_summary__isnull=False).exclude(refined_summary='').order_by('order', 'created_at')
        
        full_text = f"{self.name}"
        if self.subject:
            full_text += f" - {self.subject}"
        full_text += "\n" + "="*50 + "\n\n"
        
        for topic in topics:
            full_text += f"📚 {topic.title}\n"
            if topic.page_range:
                full_text += f"Pages: {topic.page_range}\n"
            full_text += "\n" + topic.refined_summary + "\n\n"
            full_text += "-"*50 + "\n\n"
        
        return full_text


class Topic(BaseModel):
    """Represents a topic within a course (e.g., 'Cell Structure - Pages 1-3')"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=300)  # e.g., "Cell Membrane & Transport"
    raw_text = models.TextField(blank=True)   # OCR extracted text
    refined_summary = models.TextField(blank=True)  # Polished summary from ChatGPT
    page_range = models.CharField(max_length=50, blank=True)  # e.g., "Pages 5-8"
    order = models.IntegerField(default=0)  # For manual ordering
    
    class Meta:
        ordering = ['course', 'order', 'created_at']
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    def is_refined(self):
        """Check if topic has refined summary"""
        return bool(self.refined_summary and self.refined_summary.strip())
    
    def get_status(self):
        """Get status badge"""
        return "✓ Refined" if self.is_refined() else "✏ Raw Only"


# Keep old models for backward compatibility (optional - can delete later)
class Document(BaseModel):
    """Legacy model - can be deleted after migration"""
    image_paths = models.JSONField(default=list)
    pages_count = models.PositiveIntegerField(default=0)
    extracted_text = models.TextField(blank=True)
    ocr_completed = models.BooleanField(default=False)


class AIOutput(BaseModel):
    """Legacy model - can be deleted after migration"""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='ai')
    summary = models.TextField(blank=True)
    key_points = models.TextField(blank=True)
    questions = models.TextField(blank=True)
    answers = models.TextField(blank=True)
    processed = models.BooleanField(default=False)