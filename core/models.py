# ==================== core/models.py ====================
"""
Core models including custom AdminUser for backend authentication
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class AdminUserManager(BaseUserManager):
    """Manager for AdminUser model"""
    
    def create_user(self, username, password=None, **extra_fields):
        """Create and return a regular admin user"""
        if not username:
            raise ValueError('Username is required')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(username, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for backend administrators.
    Separate from PremiumUser (which is for frontend users).
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Username for login"
    )
    
    full_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Full name of the admin"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Can this user login?"
    )
    
    is_staff = models.BooleanField(
        default=True,
        help_text="Can access Django admin"
    )
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Fix the clash with auth.User by adding related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='admin_users',
        related_query_name='admin_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='admin_users',
        related_query_name='admin_user',
    )
    
    objects = AdminUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    @property
    def display_name(self):
        """Return full name if available, otherwise username"""
        return self.full_name if self.full_name else self.username