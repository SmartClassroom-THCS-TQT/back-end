from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Teacher, Admin, Student


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # list_display: xác định các trường sẽ được hiển thị trong danh sách người dùng trên giao diện admin
    list_display = ['user_id', 'email', 'role', 'is_active', 'is_staff', 'is_superuser']  # Hiển thị các thông tin quan trọng trong danh sách

    # list_filter: cho phép lọc danh sách người dùng theo các trường này
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']  # Có thể lọc người dùng theo role và các quyền

    # search_fields: cho phép tìm kiếm người dùng dựa trên các trường này
    search_fields = ['email', 'user_id']  # Tìm kiếm bằng email hoặc user_id

    # readonly_fields: xác định các trường mà không thể chỉnh sửa từ giao diện admin
    readonly_fields = ['date_joined', 'last_login']  # Không cho phép sửa đổi ngày tham gia và lần đăng nhập cuối

    # fieldsets: xác định cách nhóm các trường trong form khi chỉnh sửa người dùng
    # fieldsets = (
    #     (None, {'fields': ('password')}),  # Nhóm mật khẩu người dùng
    #     ('Personal info', {'fields': ('email', 'phone_number', 'role')}),  # Thông tin cá nhân, gồm email, số điện thoại và vai trò
    #     ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),  # Quyền hạn người dùng
    # )
    
    # add_fieldsets: xác định các trường hiển thị khi tạo người dùng mới
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # Đảm bảo form tạo mới có chiều rộng đầy đủ
            'fields': ('password1', 'password2', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')  # Các trường khi tạo người dùng
        }),
    )
    
    # filter_horizontal: dùng để hiển thị danh sách lựa chọn với các trường quan hệ nhiều-nhiều (nếu có), mặc dù không dùng trong trường hợp này
    filter_horizontal = ()  # Không sử dụng trường hợp này, vì không có quan hệ nhiều-nhiều
    ordering=['user_id'] # Sắp xếp người dùng theo user_id



# Teacher Admin
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_id', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels']
    search_fields = ['full_name', 'user__user_id']
    list_filter = ['active_status', 'contract_types', 'expertise_levels']

# Admin Admin
class AdminAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_id', 'sex', 'day_of_birth', 'nation', 'active_status', 'contract_types', 'expertise_levels', 'description']
    search_fields = ['full_name', 'user__user_id']
    list_filter = ['active_status', 'contract_types', 'expertise_levels']

# Student Admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_id', 'sex', 'day_of_birth', 'nation', 'active_status']
    search_fields = ['full_name', 'user__user_id']
    list_filter = ['active_status']

# Register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Student, StudentAdmin)
