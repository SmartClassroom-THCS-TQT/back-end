from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Teacher, Admin, Student

# CustomUserAdmin để quản lý CustomUser trong Django Admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Teacher, Admin, Student

class CustomUserAdmin(UserAdmin):
    # Các trường hiển thị trong danh sách người dùng
    list_display = ('user_id', 'email', 'phone_number', 'role', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    
    # Các trường có thể lọc
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    
    # Các trường có thể tìm kiếm
    search_fields = ('user_id', 'email', 'phone_number', 'full_name')
    
    # Sắp xếp mặc định
    ordering = ('user_id',)

    # Các nhóm trường hiển thị trong trang chi tiết người dùng
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'sex', 'day_of_birth', 'nation', 'active_status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role')}),
        # Loại bỏ 'last_login' và 'date_joined' khỏi fieldsets
    )

    # Các trường hiển thị khi thêm người dùng mới
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'email', 'phone_number', 'password1', 'password2', 'role', 'full_name', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )


# TeacherAdmin để quản lý Teacher trong Django Admin
class TeacherAdmin(admin.ModelAdmin):
    # Các trường hiển thị trong danh sách giáo viên
    list_display = ('get_teacher_id', 'full_name', 'contract_types', 'expertise_levels')
    
    # Các trường có thể tìm kiếm
    search_fields = ('user__user_id', 'user__full_name')
    
    # Phương thức để lấy teacher_id
    def get_teacher_id(self, obj):
        return obj.user.user_id
    get_teacher_id.short_description = 'Teacher ID'
    
    # Phương thức để lấy full_name từ CustomUser
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Full Name'

# AdminAdmin để quản lý Admin trong Django Admin
class AdminAdmin(admin.ModelAdmin):
    # Các trường hiển thị trong danh sách admin
    list_display = ('get_admin_id', 'full_name', 'contract_types', 'expertise_levels', 'description')
    
    # Các trường có thể tìm kiếm
    search_fields = ('user__user_id', 'user__full_name')
    
    # Phương thức để lấy admin_id
    def get_admin_id(self, obj):
        return obj.user.user_id
    get_admin_id.short_description = 'Admin ID'
    
    # Phương thức để lấy full_name từ CustomUser
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Full Name'

# StudentAdmin để quản lý Student trong Django Admin
class StudentAdmin(admin.ModelAdmin):
    # Các trường hiển thị trong danh sách học sinh
    list_display = ('get_student_id', 'full_name', 'classroom')
    
    # Các trường có thể tìm kiếm
    search_fields = ('user__user_id', 'user__full_name')
    
    # Phương thức để lấy student_id
    def get_student_id(self, obj):
        return obj.user.user_id
    get_student_id.short_description = 'Student ID'
    
    # Phương thức để lấy full_name từ CustomUser
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = 'Full Name'

# Đăng ký các model với Django Admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Student, StudentAdmin)