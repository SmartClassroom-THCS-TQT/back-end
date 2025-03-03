from django.contrib import admin
from .models import Room, Semester, Subject, Time_slot, Session, Teacher_assignment

# Admin for Room model
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('code', 'name', 'manager')
#     search_fields = ('code', 'name')
#     readonly_fields = ('code',)  # 'code' is a primary key and should not be editable
#     list_filter = ('manager',)
    
#     def get_students(self, obj):
#         return obj.get_students().count()
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'student_count')

    def student_count(self, obj):
        return obj.get_capacity()
    student_count.short_description = 'Number of Students'

# Admin for Semester model
# class SemesterAdmin(admin.ModelAdmin):
#     list_display = ('code', 'start_date', 'weeks_count', 'end_date')
#     search_fields = ('code',)
#     readonly_fields = ('code', 'start_date', 'weeks_count', 'end_date')  # 'code' is primary key, 'start_date' and 'weeks_count' are defined
#     list_filter = ('start_date',)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['code', 'start_date', 'weeks_count', 'end_date']
    search_fields = ['code', 'start_date']

    # Thêm form validation tại đây nếu cần
    def save_model(self, request, obj, form, change):
        if obj.weeks_count is None:
            raise ValueError('Weeks count cannot be None')
        super().save_model(request, obj, form, change)

# Admin for Subject model
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    readonly_fields = ('code',)  # 'code' is primary key and should not be editable


# Admin for Time_slot model
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_time', 'end_time')
    search_fields = ('code', 'start_time', 'end_time')
    

# Admin for Session model
class SessionAdmin(admin.ModelAdmin):
    list_display = ('semester_code', 'subject_code', 'room_code', 'day', 'time_slot', 'teacher', 'lesson_number', 'lesson_name', 'grade', 'absences', 'status')
    search_fields = ('semester_code__name', 'subject_code__name', 'room_code__name', 'teacher__name', 'lesson_name')
    list_filter = ('semester_code', 'subject_code', 'room_code', 'teacher', 'grade', 'status')
    ordering = ('day', 'time_slot')
    fieldsets = (
        (None, {
            'fields': ('semester_code', 'subject_code', 'room_code', 'day', 'time_slot', 'teacher', 'lesson_number', 'lesson_name')
        }),
        ('Additional Info', {
            'fields': ('detail', 'document', 'comment', 'grade', 'absences', 'status')
        }),
    )


# Admin for Teacher_assignment model
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject_code', 'semester_code', 'room_code')
    search_fields = ('teacher__user_id', 'subject_code__name', 'semester_code__code', 'room_code__name')
    readonly_fields = ('semester_code', 'subject_code', 'room_code', 'teacher')  # These fields are assigned and shouldn't be edited

# Register all models with their respective admin
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Time_slot, TimeSlotAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Teacher_assignment, TeacherAssignmentAdmin)
