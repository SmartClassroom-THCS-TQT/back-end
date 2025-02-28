from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, user_id, role, password=None, **extra_fields):
        if not user_id:
            raise ValueError('models messenger: User ID is required')
        if not role:
            raise ValueError('models messenger: Role is required')

        extra_fields.setdefault("is_active", True)

        user = self.model(user_id=user_id, role=role, **extra_fields)
        user.set_password(password or user_id)  
        user.save(using=self._db)
        return user


    def create_superuser(self, user_id, role='admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        superuser = self.model(user_id=user_id, role=role, **extra_fields)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    user_id = models.CharField(primary_key=True, max_length=16, editable=False)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    role = models.CharField(max_length=32, choices=USER_ROLE_CHOICES)

    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=32, null=True, blank=True)
    day_of_birth = models.DateField(null=True, blank=True)
    nation = models.CharField(max_length=32, null=True, blank=True)
    active_status = models.CharField(max_length=355, null=True, blank=True)
    
    # User permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.user_id

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser,primary_key=True, on_delete=models.CASCADE, related_name='teacher')
    contract_types= models.CharField(max_length=255, null=True, blank=True)
    expertise_levels = models.CharField(max_length=255, null=True, blank=True)
    subjects = models.TextField(null=True, blank=True)
    def get_teacher_id(self):
        return self.user.user_id
    def __str__(self):
        return f"{self.user.full_name} - {self.user.user_id}"
    class Meta:
        db_table = 'Teacher'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

class Admin(models.Model):
    user = models.OneToOneField(CustomUser,primary_key=True, on_delete=models.CASCADE,related_name='admin')
    contract_types= models.CharField(max_length=255, null=True, blank=True)
    expertise_levels = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=32, null=True, blank=True)
    def get_admin_id(self):
        return self.user.user_id
    def __str__(self):
        return f"{self.user.full_name} - {self.user.user_id}"
    class Meta:
        db_table = 'Admin'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

  
class Student(models.Model):
    user = models.OneToOneField(CustomUser,primary_key=True, on_delete=models.CASCADE,related_name='student')
    classroom = models.ForeignKey('managements.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='students')
    def get_student_id(self):
        return self.user.user_id
    def __str__(self):
        return f"{self.user.full_name} - {self.user.user_id}"
    class Meta:
        db_table = 'Student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'




