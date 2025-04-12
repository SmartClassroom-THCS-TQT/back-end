from django.db import models
from django.core.exceptions import ValidationError
class Seating(models.Model):
    student = models.OneToOneField('users.Student',on_delete=models.CASCADE, related_name='seating')
    room = models.ForeignKey('managements.Room', on_delete=models.CASCADE, related_name='seatings')
    # mặc dù hs đã được liên kết với room, nhưng hs có thể có nhiều chỗ ngồi ở các lớp khác nhau đó
    row = models.IntegerField()
    column = models.IntegerField()

    class Meta:
        db_table = 'seating'
        verbose_name = 'Seating'
        verbose_name_plural = 'Seatings'
        unique_together = ('room', 'row', 'column')  # Mỗi chỗ ngồi duy nhất trong phòng
        ordering = ['room', 'row', 'column']

    def __str__(self):
        return f"{self.student.full_name} - Room {self.room.name} at ({self.row}, {self.column})"
    
class Attendance(models.Model):
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='attendances')
    session = models.ForeignKey('managements.Session', on_delete=models.CASCADE, related_name='attendances')
    status = models.BooleanField(null=True, blank=True)
    attendance_time = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        db_table = 'attendance'
        verbose_name = 'Điểm danh'
        verbose_name_plural = 'Danh sách điểm danh'
        unique_together = ('student', 'session')  


    def clean(self):
        # Kiểm tra xem người dùng (student) có phải là sinh viên không
        if not self.student.account.role == 'student':
            raise ValidationError('User must be a student.')

    def save(self, *args, **kwargs):
        self.clean()  # Kiểm tra trước khi lưu
        super().save(*args, **kwargs)  # Lưu đối tượng

    def __str__(self):
        return f"{self.student} - {self.session} - {'Có mặt' if self.status else 'Vắng mặt'}"
    
    
class Device(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    room = models.ForeignKey('managements.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='devices')
    class Meta:
        db_table = 'device'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'

    def __str__(self):
        return self.code