from django.contrib import admin
from .models import CustomUser, Teacher, Admin, Student
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'full_name', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('user_id', 'full_name', 'email')
    readonly_fields = ('user_id','password', 'date_joined', 'last_login')  # Fields that should be read-only
    exclude = ('groups','user_permissions')  # Fields that should be excluded from the form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        # Make fields read-only if obj exists (i.e. editing an existing object)
        if obj:
            for fieldset in fieldsets:
                # fieldset[1] contains the fields of the current section
                for field in fieldset[1]:
                    # Check if the field is one of the fields that should be readonly
                    if field == 'user_id' or field == 'date_joined' or field == 'last_login':
                        # Set this field to be readonly
                        fieldsets[0][1] = tuple(
                            f for f in fieldset[1] if f != field
                        ) + (field,)
        return fieldsets

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_id', 'user', 'contract_types', 'expertise_levels', 'subjects')
    list_filter = ('contract_types', 'expertise_levels')
    search_fields = ('user__user_id', 'user__full_name', 'contract_types', 'expertise_levels')
    readonly_fields = ('get_teacher_id', 'user')  # Fields that should be read-only

# class AdminAdmin(admin.ModelAdmin):
#     list_display = ('get_admin_id', 'user', 'contract_types', 'expertise_levels', 'description')
#     list_filter = ('contract_types', 'expertise_levels')
#     search_fields = ('user__user_id', 'user__full_name', 'contract_types', 'expertise_levels', 'description')
#     readonly_fields = ('get_admin_id', 'user')  # Fields that should be read-only

class AdminAdmin(admin.ModelAdmin):
    list_display = ('get_admin_id', 'user', 'contract_types', 'expertise_levels', 'description')
    list_filter = ('contract_types', 'expertise_levels')
    search_fields = ('user__user_id', 'user__full_name', 'contract_types', 'expertise_levels', 'description')
    readonly_fields = ('get_admin_id', 'user')  # Fields that should be read-only
    
    def get_admin_id(self, obj):
        return obj.user.user_id  # Chắc chắn rằng phương thức này trả về giá trị hợp lệ
    get_admin_id.short_description = 'Admin ID'  # Tùy chỉnh tiêu đề của cột
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_student_id', 'user', 'classroom')
    list_filter = ('classroom',)
    search_fields = ('user__user_id', 'user__full_name', 'classroom__name')
    readonly_fields = ('get_student_id', 'user')  # Fields that should be read-only



# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Admin, AdminAdmin)
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