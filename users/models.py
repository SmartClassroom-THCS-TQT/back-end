from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group

class AccountManager(BaseUserManager):
    def create_user(self, user_id, username, role, password=None, **extra_fields):
        if not user_id:
            raise ValueError('User ID is required')
        if not username:
            raise ValueError('Username is required')
        if not role:
            raise ValueError('Role is required')

        extra_fields.setdefault("is_active", True)

        user = self.model(user_id=user_id, username=username, role=role, **extra_fields)
        user.set_password(password or user_id)  # Nếu không có mật khẩu, dùng user_id làm mật khẩu mặc định
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # Đặt các giá trị mặc định cho superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Mặc định role là 'admin' cho superuser
        extra_fields.setdefault('user_id', username)  # Mặc định user_id bằng username

        # Tạo superuser
        superuser = self.model(
            username=username,  # Truyền username
            **extra_fields  # Truyền tất cả các trường khác từ extra_fields
        )
        superuser.set_password(password)  # Đặt mật khẩu
        superuser.save(using=self._db)  # Lưu superuser vào database

        return superuser



class Account(AbstractBaseUser, PermissionsMixin):
    USER_ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    user_id = models.CharField(primary_key=True, max_length=16, editable=False)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=32, choices=USER_ROLE_CHOICES)

    
    # User permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.user_id} - {self.username} - {self.role}"
    class Meta:
        db_table = 'account'
        verbose_name = 'All-Account'
        verbose_name_plural = 'Accounts'
        ordering = ['user_id','username']  

class Teacher(models.Model):
    account = models.OneToOneField(Account,primary_key=True, on_delete=models.CASCADE, related_name='teacher')

    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True) 
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=32, null=True, blank=True)
    day_of_birth = models.DateField(null=True, blank=True)
    nation = models.CharField(max_length=32, null=True, blank=True)
    active_status = models.CharField(max_length=355, null=True, blank=True)
    contract_types= models.CharField(max_length=255, null=True, blank=True)
    expertise_levels = models.CharField(max_length=255, null=True, blank=True)
    subjects = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='profile-images/', null=True, blank=True)
    def get_teacher_id(self):
        return self.account.user_id
    def __str__(self):
        return f"{self.full_name} - {self.account.user_id}"
    class Meta:
        db_table = 'teacher'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['full_name']  # Sắp xếp theo tên đầy đủ của người dùng

class Admin(models.Model):
    account = models.OneToOneField(Account,primary_key=True, on_delete=models.CASCADE,related_name='admin')

    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True) 
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=32, null=True, blank=True)
    day_of_birth = models.DateField(null=True, blank=True)
    nation = models.CharField(max_length=32, null=True, blank=True)
    active_status = models.CharField(max_length=355, null=True, blank=True)
    contract_types= models.CharField(max_length=255, null=True, blank=True)
    expertise_levels = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=32, null=True, blank=True)
    image = models.ImageField(upload_to='profile-images/', null=True, blank=True)
    def get_admin_id(self):
        return self.account.user_id
    def __str__(self):
        return f"{self.full_name} - {self.account.user_id}"
    class Meta:
        db_table = 'admin'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        ordering = ['full_name']  # Sắp xếp theo tên đầy đủ của người dùng

  
class Student(models.Model):
    account = models.OneToOneField(Account,primary_key=True, on_delete=models.CASCADE,related_name='student')

    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True) 
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    # room = models.ForeignKey('managements.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='students')
    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=32, null=True, blank=True)
    day_of_birth = models.DateField(null=True, blank=True)
    nation = models.CharField(max_length=32, null=True, blank=True)
    active_status = models.CharField(max_length=355, null=True, blank=True)
    image = models.ImageField(upload_to='profile-images/', null=True, blank=True)
    def get_student_id(self):
        return self.account.user_id
    def __str__(self):
        return f"{self.full_name} - {self.account.user_id}"
    class Meta:
        db_table = 'student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['full_name']  



