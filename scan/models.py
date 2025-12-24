from django.db import models
from core.models import BaseModel


class Department(BaseModel):
    """Represents a department/subject area (e.g., Health Science, Engineering)"""
    name = models.CharField(max_length=200, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_department(cls, name):
        """Get existing or create new department (case-insensitive)"""
        if not name or not name.strip():
            return None
        name = name.strip()
        dept, created = cls.objects.get_or_create(name__iexact=name, defaults={'name': name})
        return dept


class Course(BaseModel):
    """Represents a course (e.g., BIO 202, CHEM 101)"""
    name = models.CharField(max_length=200)
    departments = models.ManyToManyField(Department, blank=True, related_name='courses')
    year = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total_topics(self):
        return self.topics.count()
    
    def get_refined_count(self):
        return self.topics.filter(refined_summary__isnull=False).exclude(refined_summary='').count()
    
    def get_departments_display(self):
        """Return comma-separated department names"""
        return ", ".join([d.name for d in self.departments.all()])
    
    def get_full_refined_text(self):
        """Combine all refined summaries in order"""
        topics = self.topics.filter(
            refined_summary__isnull=False
        ).exclude(refined_summary='').order_by('order', 'created_at')
     
        # Header
        full_text = f"{self.name}\n"
        dept_display = self.get_departments_display()
        if dept_display:
            full_text += f"{dept_display}\n"
        if self.year:
            full_text += f"Year: {self.year}\n"
        full_text += "=" * 50 + "\n\n"
        
        # Topics
        for topic in topics:
            full_text += f"📚 {topic.title}\n"
            if topic.page_range:
                full_text += f"Pages: {topic.page_range}\n"
            full_text += "\n" + topic.refined_summary + "\n\n"
            full_text += "-" * 50 + "\n\n"
        
        return full_text


class Topic(BaseModel):
    """Represents a topic within a course (e.g., 'Cell Structure - Pages 1-3')"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=300)
    raw_text = models.TextField(blank=True)
    refined_summary = models.TextField(blank=True)
    page_range = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
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

class AIRefine(BaseModel):
    """Stores AI-generated refined summaries from different providers"""
    
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('groq', 'Groq Llama'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='ai_refines')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    refined_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    qa_count = models.IntegerField(default=0)  # number of Q&As generated
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['topic', 'provider']  # One refine per provider per topic
    
    def __str__(self):
        return f"{self.topic.title} - {self.get_provider_display()} ({self.status})"
    
    def is_successful(self):
        return self.status == 'completed' and bool(self.refined_text)