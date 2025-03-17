from django.contrib import admin
from .models import Account, Teacher, Admin, Student
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('user_id', 'username', 'role')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    ordering = ['username']

    # Chỉ định các trường chỉ đọc
    readonly_fields = ('user_id',)

    # Sử dụng fieldsets để nhóm các trường (loại bỏ user_id khỏi fields)
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('username', 'role')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Quyền và Nhóm', {  # Thêm phần mới cho Group và Permission
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)  # Thu gọn phần này (tùy chọn)
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(Account, AccountAdmin)

# TeacherAdmin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name','email', 'get_teacher_id', 'phone_number', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels')
    search_fields = ('full_name','email', 'phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation')
    ordering = ['full_name']
    

    def get_teacher_id(self, obj):
        return obj.get_teacher_id()
    get_teacher_id.admin_order_field = 'user__user_id'
    get_teacher_id.short_description = 'Teacher ID'

admin.site.register(Teacher, TeacherAdmin)

# AdminAdmin
class AdminAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email','get_admin_id', 'phone_number', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels', 'description')
    search_fields = ('full_name','email', 'phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation')
    ordering = ['full_name']
  

    def get_admin_id(self, obj):
        return obj.get_admin_id()
    get_admin_id.admin_order_field = 'user__user_id'
    get_admin_id.short_description = 'Admin ID'

admin.site.register(Admin, AdminAdmin)

# StudentAdmin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email','get_student_id', 'phone_number', 'room', 'sex', 'day_of_birth', 'nation', 'active_status')
    search_fields = ('full_name', 'email','phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation', 'room')
    ordering = ['full_name']
    

    def get_student_id(self, obj):
        return obj.get_student_id()
    get_student_id.admin_order_field = 'user__user_id'
    get_student_id.short_description = 'Student ID'

admin.site.register(Student, StudentAdmin)



#-------------------------------------------------------------------------------------------------------------------
# Đăng ký lại GroupAdmin để hiển thị người dùng trong mỗi nhóm
class CustomGroupAdmin(GroupAdmin):
    # Tùy chỉnh danh sách các trường cần hiển thị trong admin
    list_display = ('name', 'get_users')  # Thêm 'get_users' để hiển thị người dùng trong nhóm
    
    # Hàm để hiển thị người dùng thuộc nhóm
    def get_users(self, obj):
        return ", ".join([user.username for user in obj.user_set.all()])
    
    get_users.short_description = 'Users'  # Đặt tiêu đề cho cột người dùng

# Đăng ký lại admin cho bảng Permission (quyền)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    search_fields = ('name', 'codename')



# Đăng ký các bảng trong admin
admin.site.register(Permission, PermissionAdmin)
admin.site.unregister(Group)  # Hủy đăng ký Group mặc định
admin.site.register(Group, CustomGroupAdmin)  # Đăng ký lại với GroupAdmin tùy chỉnh