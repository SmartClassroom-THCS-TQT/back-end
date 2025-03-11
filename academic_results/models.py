from django.db import models

# Mô hình liên kết với học sinh (Student) và môn học (Subject)
class Grade(models.Model):
    # Các loại điểm cố định
    GRADE_CHOICES = [
        ('quick_test', 'Điểm test nhanh (15 phút)'),
        ('quiz', 'Điểm kiểm tra'),
        ('midterm', 'Điểm thi giữa kỳ'),
        ('final_exam', 'Điểm thi cuối kỳ'),
        ('custom', 'Điểm tùy chỉnh')  # Loại điểm cho phép người dùng tùy chỉnh tên
    ]
    semester = models.ForeignKey('managements.Semester', on_delete=models.CASCADE, related_name='grades')  # Học kỳ
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='grades')  # Liên kết với học sinh
    subject = models.ForeignKey('managements.Subject', on_delete=models.CASCADE, related_name='grades')  # Liên kết với môn học
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Điểm của học sinh, có thể chứa điểm thập phân
    grade_type = models.CharField(max_length=20, choices=GRADE_CHOICES, default='quick_test')
    custom_grade_type = models.CharField(max_length=100, null=True, blank=True)  # Cho phép người dùng nhập loại điểm tùy chỉnh
    date_assigned = models.DateField(null=True, blank=True)  # Ngày chấm điểm

    class Meta:
        db_table = 'grade'
        verbose_name = 'Điểm'
        verbose_name_plural = 'Điểm của học sinh'
        unique_together = ('student', 'subject', 'semester')  # Mỗi học sinh có một điểm duy nhất cho mỗi môn học và học kỳ

    def save(self, *args, **kwargs):
        # Nếu grade_type là "custom" mà không có custom_grade_type, thì sẽ raise lỗi
        if self.grade_type == 'custom' and not self.custom_grade_type:
            raise ValueError('Vui lòng nhập tên loại điểm cho điểm tùy chỉnh.')
        super().save(*args, **kwargs)

    def __str__(self):
        grade_type_display = self.custom_grade_type if self.grade_type == 'custom' else dict(self.GRADE_CHOICES).get(self.grade_type, '')
        return f"{self.student} - {self.subject} - {grade_type_display} - {self.score}"

