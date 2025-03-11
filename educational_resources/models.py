
# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

# Các loại tài liệu cho phép
DOCUMENT_TYPE_CHOICES = [
    ('lesson_plan', 'Giáo án'),
    ('slide', 'Slide bài giảng'),
    ('homework', 'Bài tập'),
    ('exam', 'Đề thi'),
    ('other', 'Tài liệu khác'),
]

class Document(models.Model):
    title = models.CharField(max_length=255)  # Tiêu đề tài liệu
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)  # Loại tài liệu
    file = models.FileField(upload_to='documents/', blank=True, null=True)  # Tệp tài liệu tải lên
    description = models.TextField(blank=True, null=True)  # Mô tả tài liệu
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='documents')  # Giáo viên tải lên tài liệu
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Ngày tải lên

    # Quyền truy cập tài liệu
    access_type = models.CharField(
        max_length=10,
        choices=[('public', 'Công khai'), ('restricted', 'Hạn chế')],
        default='public',
    )
    allowed_groups = models.ManyToManyField(
        'auth.Group',  # Liên kết với nhóm người dùng có quyền xem tài liệu
        blank=True,
        related_name='allowed_documents'
    )

    class Meta:
        db_table = 'document'
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu chia sẻ'

    def __str__(self):
        return f"{self.title} - {self.document_type}"

