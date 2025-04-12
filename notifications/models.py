from django.db import models

# Create your models here.
class NotificationType(models.Model):
    """Loại thông báo"""
    name = models.CharField(max_length=100)  # Ví dụ: "Lịch học", "Điểm số", "Thông báo hệ thống", v.v.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    recipient = models.ManyToManyField('users.Account', related_name="notifications")  # Nhiều người nhận có thể nhận thông báo này
    message = models.TextField()  # Nội dung thông báo
    read = models.BooleanField(default=False)  # Trạng thái đã đọc
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian gửi thông báo
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)  # Loại thông báo
    object_id = models.PositiveIntegerField(null=True, blank=True)  # ID của đối tượng liên kết (ví dụ: session, test, event, v.v.)
    content_type = models.CharField(max_length=100, null=True, blank=True)  # Kiểu đối tượng (Ví dụ: "Session", "Exam", "Event")

    def __str__(self):
        return f"Notification to {', '.join([user.username for user in self.recipient.all()])} - {self.created_at}"

    class Meta:
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'