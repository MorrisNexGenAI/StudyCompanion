
# ==================== models_functions/department_model.py ====================
"""
Department model - Represents a department/subject area
"""
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

