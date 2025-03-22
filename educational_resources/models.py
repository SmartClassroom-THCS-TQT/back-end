
# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Tên loại tài liệu
    description = models.TextField(blank=True, null=True)  # Mô tả về loại tài liệu

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type'
        verbose_name = 'Loại tài liệu'
        verbose_name_plural = 'Các loại tài liệu'

class Document(models.Model):
    title = models.CharField(max_length=255)  # Tiêu đề tài liệu
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE,db_index=True)  # Loại tài liệu
    file = models.FileField(upload_to='documents/', blank=True, null=True)  # Tệp tài liệu tải lên
    description = models.TextField(blank=True, null=True)  # Mô tả tài liệu
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='documents',db_index=True)  # Giáo viên tải lên tài liệu
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Ngày tải lên

    rooms = models.ManyToManyField('managements.Room', blank=True, related_name='documents')
    subjects = models.ManyToManyField('managements.Subject', blank=True, related_name='documents')
    # Quyền truy cập tài liệu
    access_type = models.CharField(
        max_length=10,
        choices=[('public', 'Công khai'), ('restricted', 'Hạn chế')],
        default='public',
        db_index=True,
    )
    allowed_groups = models.ManyToManyField(
        'auth.Group',  # Liên kết với nhóm người dùng có quyền xem tài liệu
        blank=True,
        related_name='allowed_documents'
    )
    allowed_users = models.ManyToManyField(
        'users.Student', blank=True, related_name='allowed_individual_documents'
    )
    is_active = models.BooleanField(default=True)  # Xoá mềm hoặc ẩn tài liệu
    archived = models.BooleanField(default=False)  # Đánh dấu lưu trữ
    # Optional: Gắn thẻ
    tags = models.ManyToManyField(
        'Tag', blank=True, related_name='documents'
    )
    @property
    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

    class Meta:
        db_table = 'document'
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'

    def __str__(self):
        return f"{self.title} - {self.document_type.name}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tag'
        verbose_name = 'Thẻ'
        verbose_name_plural = 'Thẻ tài liệu'

    def __str__(self):
        return self.name