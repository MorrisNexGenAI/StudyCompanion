
# ==================== models_functions/course_model.py ====================
"""
Course model - Represents a course (e.g., BIO 202, CHEM 101)
"""
from django.db import models
from core.models import BaseModel
from .department_model import Department


class Course(BaseModel):
    """Represents a course (e.g., BIO 202, CHEM 101)"""
    name = models.CharField(max_length=200)
    departments = models.ManyToManyField(Department, blank=True, related_name='courses')
    year = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)  # SOFT DELETE
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_total_topics(self):
        return self.topics.filter(is_deleted=False).count()
    
    def get_refined_count(self):
        return self.topics.filter(is_deleted=False, refined_summary__isnull=False).exclude(refined_summary='').count()
    
    def get_departments_display(self):
        """Return comma-separated department names"""
        return ", ".join([d.name for d in self.departments.all()])
    
    def get_full_refined_text(self):
        """Combine all refined summaries in order"""
        topics = self.topics.filter(
            is_deleted=False,
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
    
    def soft_delete(self):
        """Soft delete course and all its topics"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])
        # Also soft delete all topics
        self.topics.update(is_deleted=True)


