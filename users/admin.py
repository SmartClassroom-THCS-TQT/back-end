from django.contrib import admin
from .models import Account, Teacher, Admin, Student
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    search_fields = ('user_id', 'email', 'role')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    ordering = ['email']


admin.site.register(Account, AccountAdmin)

# TeacherAdmin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_teacher_id', 'phone_number', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels')
    search_fields = ('full_name', 'phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation')
    ordering = ['full_name']
    

    def get_teacher_id(self, obj):
        return obj.get_teacher_id()
    get_teacher_id.admin_order_field = 'user__user_id'
    get_teacher_id.short_description = 'Teacher ID'

admin.site.register(Teacher, TeacherAdmin)

# AdminAdmin
class AdminAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_admin_id', 'phone_number', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels', 'description')
    search_fields = ('full_name', 'phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation')
    ordering = ['full_name']
  

    def get_admin_id(self, obj):
        return obj.get_admin_id()
    get_admin_id.admin_order_field = 'user__user_id'
    get_admin_id.short_description = 'Admin ID'

admin.site.register(Admin, AdminAdmin)

# StudentAdmin
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_student_id', 'phone_number', 'classroom', 'sex', 'day_of_birth', 'nation', 'active_status')
    search_fields = ('full_name', 'phone_number', 'sex', 'nation', 'active_status')
    list_filter = ('active_status', 'sex', 'nation', 'classroom')
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