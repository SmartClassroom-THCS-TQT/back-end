from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Student, Admin, Teacher

@receiver(post_delete, sender=Student)
@receiver(post_delete, sender=Admin)

@receiver(post_delete, sender=Teacher)
def delete_account(sender, instance, **kwargs):
    """
    Xóa account khi xóa một trong các đối tượng liên quan như Student, Admin, Parent, Teacher
    """
    if instance.account:
        instance.account.delete()
