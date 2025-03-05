from django.db import models
class Seating(models.Model):
    student = models.OneToOneField(
        'accounts.Student', 
        primary_key=True,
        on_delete=models.CASCADE, 
        related_name='seating'
    )
    room = models.ForeignKey(
        'managements.Room',
        on_delete=models.CASCADE, 
        related_name='seatings'
    )
    row = models.IntegerField()
    column = models.IntegerField()

    class Meta:
        db_table = 'seating'
        verbose_name = 'Seating Position'
        verbose_name_plural = 'Seating Positions'
        unique_together = ('room', 'row', 'column') 

    def __str__(self):
         return f"Student {self.student.full_name} in Room {self.room.name} at position ({self.row}, {self.column})"
    
# class Attendance(models.Model):
#     STATUS_CHOICES = [
#         (1, 'Có mặt'),
#         (2, 'Đi muộn'),
#         (3, 'Vắng mặt'),
#     ]   

#     user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='attendances')
#     lesson = models.ForeignKey('adminpanel.Lesson', on_delete=models.CASCADE, related_name='attendances')
#     status = models.IntegerField(choices=STATUS_CHOICES, null=True, blank=True)
#     attendance_time = models.DateTimeField(auto_now_add=True)  
    
#     class Meta:
#         db_table = 'attendance'
#         verbose_name = 'Điểm danh'
#         verbose_name_plural = 'Danh sách điểm danh'
#         unique_together = ('user', 'lesson')

#     def clean(self):
#         if not self.user.is_student:
#             raise ValidationError('User must be a student.')

#     def save(self, *args, **kwargs):
#         self.clean()  
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user} - {self.lesson} - {self.get_status_display()}"
    
    
    
# class Device(models.Model):
#     device_id = models.CharField(max_length=50, primary_key=True)
#     room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, blank=True, related_name='devices')

#     def __str__(self):
#         return self.device_id