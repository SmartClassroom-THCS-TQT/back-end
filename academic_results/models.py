from django.db import models
from django.core.exceptions import ValidationError


class GradeType(models.Model):
    name = models.CharField(max_length=100)  # Tên loại điểm
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)  # Hệ số điểm
    is_global = models.BooleanField(default=True)  # Có phải loại điểm dùng chung hay không
    created_by = models.ForeignKey(
        'users.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_grade_types'
    )
    room = models.ForeignKey(  # Chỉ định nếu loại điểm chỉ áp dụng trong một lớp cụ thể
        'managements.Room',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_grade_types'
    )

    class Meta:
        db_table = 'grade_type'
        verbose_name = 'Loại điểm'
        verbose_name_plural = 'Các loại điểm'

    def clean(self):
        # Nếu không phải global thì phải gắn với lớp và giáo viên
        if not self.is_global and (self.room is None or self.created_by is None):
            raise ValidationError("Loại điểm local cần phải có cả 'room' và 'created_by'.")

    def __str__(self):
        return f"{self.name} ({'Toàn hệ thống' if self.is_global else 'Lớp ' + str(self.room)})"

class Grade(models.Model):
    semester = models.ForeignKey('managements.Semester', on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey('managements.Subject', on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_type = models.ForeignKey('GradeType', on_delete=models.CASCADE, related_name='grades')
    date_assigned = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'grade'
        verbose_name = 'Điểm'
        verbose_name_plural = 'Điểm của học sinh'
        # Có thể cho phép nhiều điểm cùng loại nếu cần, hoặc chỉnh sửa unique_together tùy mục đích
        # unique_together = ('student', 'subject', 'semester', 'grade_type')

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.grade_type.name} - {self.score}"
