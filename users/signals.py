from django.db.models.signals import post_delete, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Student, Admin, Teacher, Account

@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    # Tạo các nhóm người dùng
    groups = {
        'admin': 'Quản trị viên',
        'teacher': 'Giáo viên',
        'student': 'Học sinh'
    }
    
    for group_name, group_desc in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            group.description = group_desc
            group.save()

    # Lấy các ContentType
    account_content_type = ContentType.objects.get_for_model(Account)
    student_content_type = ContentType.objects.get_for_model(Student)
    teacher_content_type = ContentType.objects.get_for_model(Teacher)
    admin_content_type = ContentType.objects.get_for_model(Admin)

    # Lấy tất cả các quyền
    all_permissions = Permission.objects.all()

    # Phân quyền cho từng nhóm
    admin_group = Group.objects.get(name='admin')
    teacher_group = Group.objects.get(name='teacher')
    student_group = Group.objects.get(name='student')

    # Quyền cho admin và teacher (toàn quyền)
    full_permissions = [
        # Account permissions
        'add_account', 'change_account', 'delete_account', 'view_account',
        # Student permissions
        'add_student', 'change_student', 'delete_student', 'view_student',
        # Teacher permissions
        'add_teacher', 'change_teacher', 'delete_teacher', 'view_teacher',
        # Admin permissions
        'add_admin', 'change_admin', 'delete_admin', 'view_admin'
    ]
    
    # Gán toàn quyền cho admin
    for perm in full_permissions:
        try:
            permission = Permission.objects.get(codename=perm)
            admin_group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass

    # Gán toàn quyền cho teacher
    for perm in full_permissions:
        try:
            permission = Permission.objects.get(codename=perm)
            teacher_group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass

    # Quyền cho học sinh (chỉ xem)
    student_permissions = [
        # Account permissions
        'view_account',
        # Student permissions
        'view_student',
        # Teacher permissions
        'view_teacher',
        # Admin permissions
        'view_admin'
    ]
    for perm in student_permissions:
        try:
            permission = Permission.objects.get(codename=perm)
            student_group.permissions.add(permission)
        except Permission.DoesNotExist:
            pass

@receiver(post_delete, sender=Student)
@receiver(post_delete, sender=Admin)
@receiver(post_delete, sender=Teacher)
def delete_account(sender, instance, **kwargs):
    """
    Xóa account khi xóa một trong các đối tượng liên quan như Student, Admin, Teacher
    """
    if instance.account:
        instance.account.delete()
