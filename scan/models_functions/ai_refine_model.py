
# ==================== models_functions/ai_refine_model.py ====================
"""
AIRefine model - Stores AI-generated refined summaries
"""
from django.db import models
from core.models import BaseModel
from .topic_model import Topic


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
    processing_time = models.FloatField(null=True, blank=True)
    qa_count = models.IntegerField(default=0)
    
    # NEW FIELD - Difficulty Level
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('difficult', 'Difficult'),
        ],
        default='medium',
        help_text="Difficulty level used when generating this refinement"
    )
    
    class Meta:
        ordering = ['-created_at']
        # Updated unique_together to include difficulty
        unique_together = ['topic', 'provider', 'difficulty_level']
    
    def __str__(self):
        return f"{self.topic.title} - {self.get_provider_display()} ({self.difficulty_level}) [{self.status}]"
    
    def is_successful(self):
        return self.status == 'completed' and bool(self.refined_text)

