from django.db import models
from django.contrib.auth import get_user_model

class DeploymentLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('in_progress', 'In Progress'),
    ]

    ACTION_CHOICES = [
        ('deploy', 'Deploy'),
        ('switch_env', 'Switch Environment'),
        ('restart', 'Restart Services'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    message = models.TextField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.status} - {self.created_at}" 