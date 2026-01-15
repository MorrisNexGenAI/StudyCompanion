
# ==================== models_functions/topic_model.py ====================
"""
Topic model - Represents a topic within a course
"""
from django.db import models
from core.models import BaseModel
from .course_model import Course


class Topic(BaseModel):
    """Represents a topic within a course (e.g., 'Cell Structure - Pages 1-3')"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=300)
    raw_text = models.TextField(blank=True)
    refined_summary = models.TextField(blank=True)
    page_range = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_premium = models.BooleanField(
        default=False,
        help_text="If True, only selected premium users can access this topic"
    )
    is_deleted = models.BooleanField(default=False)  # SOFT DELETE
    
    # NEW FIELD - Difficulty Level
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy - Quick Recognition'),
            ('medium', 'Medium - Understanding'),
            ('difficult', 'Difficult - Mastery'),
        ],
        default='medium',
        help_text="Determines explanation depth and context richness for AI generation"
    )
    
    premium_users = models.ManyToManyField(
        'premium_users.PremiumUser',
        blank=True,
        related_name='accessible_topics',
        limit_choices_to={'is_active': True},
        help_text="Select users who can access this premium topic"
    )
    
    class Meta:
        ordering = ['course', 'order', 'created_at']
        indexes = [
            models.Index(fields=['is_premium']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['difficulty_level']),  # NEW INDEX
        ]
    
    def __str__(self):
        premium_badge = "🔒 " if self.is_premium else ""
        difficulty_badge = {
            'easy': '⚡',
            'medium': '📚',
            'difficult': '🎓'
        }.get(self.difficulty_level, '')
        return f"{premium_badge}{difficulty_badge} {self.course.name} - {self.title}"
    
    def is_accessible_by(self, user):
        """Check if a user can access this topic."""
        if not self.is_premium:
            return True
        
        if isinstance(user, int):
            return self.premium_users.filter(id=user, is_active=True).exists()
        else:
            return self.premium_users.filter(id=user.id, is_active=True).exists()
    
    def add_premium_user(self, user):
        """Add a user to this premium topic."""
        if not self.is_premium:
            raise ValueError("Cannot add users to community topics")
        self.premium_users.add(user)
    
    def remove_premium_user(self, user):
        """Remove a user from this premium topic."""
        self.premium_users.remove(user)
    
    def get_accessible_user_count(self):
        """Count how many active users can access this topic."""
        if not self.is_premium:
            return "All users"
        return self.premium_users.filter(is_active=True).count()
    
    def is_refined(self):
        """Check if topic has refined summary"""
        return bool(self.refined_summary and self.refined_summary.strip())
    
    def get_status(self):
        """Get status badge"""
        return "✓ Refined" if self.is_refined() else "✏ Raw Only"
    
    def soft_delete(self):
        """Soft delete topic"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])
