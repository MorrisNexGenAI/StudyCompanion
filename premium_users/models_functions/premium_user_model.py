# ==================== MODEL: premium_user_model.py ====================
"""
PremiumUser model - Premium user identified by name + 4-character code + department
"""
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import BaseModel


class PremiumUser(BaseModel):
    """
    Premium user identified by name + 4-character code + department.
    No passwords, no authentication - just identity for content filtering.
    """
    # Validator: exactly 4 alphanumeric characters
    code_validator = RegexValidator(
        regex=r'^[A-Z0-9]{4}$',
        message='Code must be exactly 4 alphanumeric characters (A-Z, 0-9).',
        code='invalid_code'
    )
    
    name = models.CharField(
        max_length=100,
        help_text="User's full name (e.g., 'Emmanuel Cooper')"
    )
    
    code = models.CharField(
        max_length=4,
        validators=[code_validator],
        help_text="Exactly 4 alphanumeric characters (e.g., 'EC21', 'AB12')"
    )
    
    # NEW FIELD: Department selection
    department = models.ForeignKey(
        'scan.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='premium_users',
        help_text="User's department - filters courses and topics"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive users cannot access premium content"
    )
    
    class Meta:
        verbose_name = "Premium User"
        verbose_name_plural = "Premium Users"
        unique_together = [('name', 'code')]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['department']),  # NEW INDEX
        ]
    
    def clean(self):
        """Validate and normalize code before saving."""
        super().clean()
        if self.code:
            # Convert to uppercase
            self.code = self.code.upper()
            # Check length
            if len(self.code) != 4:
                raise ValidationError({
                    'code': 'Code must be exactly 4 characters long.'
                })
            # Check alphanumeric
            if not self.code.isalnum():
                raise ValidationError({
                    'code': 'Code must contain only letters (A-Z) and numbers (0-9).'
                })
    
    def save(self, *args, **kwargs):
        """Ensure code is uppercase before saving."""
        if self.code:
            self.code = self.code.upper()
        self.full_clean()  # Run validators
        super().save(*args, **kwargs)
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        dept_name = f" - {self.department.name}" if self.department else ""
        return f"{self.name} ({self.code}){dept_name} {status}"
    
    @property
    def display_name(self):
        """Formatted name with code for UI display."""
        return f"{self.name} ({self.code})"
    
    @property
    def display_full(self):
        """Full display with department."""
        dept = f" - {self.department.name}" if self.department else " - No Department"
        return f"{self.name} ({self.code}){dept}"
    
    def deactivate(self):
        """Soft-delete: mark user as inactive."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
    
    def reactivate(self):
        """Restore deactivated user."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
