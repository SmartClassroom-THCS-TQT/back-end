from django.contrib import admin
from .models import CustomUser, Teacher, Admin, Student


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

class AdminAdmin(admin.ModelAdmin):
    list_display = ('get_admin_id', 'user', 'contract_types', 'expertise_levels', 'description')
    list_filter = ('contract_types', 'expertise_levels')
    search_fields = ('user__user_id', 'user__full_name', 'contract_types', 'expertise_levels', 'description')
    readonly_fields = ('get_admin_id', 'user')  # Fields that should be read-only

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
