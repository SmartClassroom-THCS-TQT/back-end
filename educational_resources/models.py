# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Tên loại tài liệu
    description = models.TextField(blank=True, null=True)  # Mô tả về loại tài liệu

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type'
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
        ordering = ['name']

class BaseDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='%(class)s_uploaded')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    rooms = models.ManyToManyField('managements.Room', blank=True, related_name='%(class)s_documents')
    subjects = models.ManyToManyField('managements.Subject', blank=True, related_name='%(class)s_documents')
    access_type = models.CharField(
        max_length=10,
        choices=[('public', 'Public'), ('restricted', 'Restricted')],
        default='public',
        db_index=True,
    )
    allowed_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='%(class)s_allowed_documents'
    )
    allowed_users = models.ManyToManyField(
        'users.Student',
        blank=True,
        related_name='%(class)s_allowed_documents'
    )
    is_active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    @property
    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

    class Meta:
        db_table = 'base_document'
        verbose_name = 'Base Document'
        verbose_name_plural = 'Base Documents'
        ordering = ['-date_uploaded']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['access_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['archived']),
        ]

class Document(BaseDocument):
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, db_index=True)

    class Meta:
        db_table = 'document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-date_uploaded']
        indexes = [
            models.Index(fields=['document_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.document_type.name}"

class LessonPlan(BaseDocument):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_lesson_plans'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'lesson_plan'
        verbose_name = 'Lesson Plan'
        verbose_name_plural = 'Lesson Plans'
        ordering = ['-date_uploaded']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reviewed_by']),
            models.Index(fields=['review_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def clean(self):
        if self.status == 'rejected' and not self.review_comment:
            raise ValidationError('A review comment is required when rejecting a lesson plan.')