from django.contrib import admin
from .models import Room, Semester, Subject, Time_slot, Session, Teacher_assignment, AcademicYear

# Admin for Room model

class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('id','year_name')  
    search_fields = ('id','year_name') 


class RoomAdmin(admin.ModelAdmin):
    list_display = ('id','academic_year', 'name', 'manager', 'student_count')

    def student_count_display(self, obj):
        return obj.students.count()
    student_count_display.short_description = 'Total Students'


class SemesterAdmin(admin.ModelAdmin):
    list_display = ['academic_year','code', 'start_date', 'weeks_count', 'end_date']
    search_fields = ['academic_year','code', 'start_date']

    # Thêm form validation tại đây nếu cần
    def save_model(self, request, obj, form, change):
        if obj.weeks_count is None:
            raise ValueError('Weeks count cannot be None')
        super().save_model(request, obj, form, change)

# Admin for Subject model
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    


# Admin for Time_slot model
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_time', 'end_time')
    search_fields = ('code', 'start_time', 'end_time')
    

# Admin for Session model
class SessionAdmin(admin.ModelAdmin):
    list_display = ('semester_code', 'subject_code', 'room_id', 'day', 'time_slot', 'teacher', 'lesson_number', 'lesson_name', 'grade', 'absences', 'status')
    search_fields = ('semester_code__name', 'subject_code__name', 'room_id__name', 'teacher__name', 'lesson_name')
    list_filter = ('semester_code', 'subject_code', 'room_id', 'teacher', 'grade', 'status')
    ordering = ('day', 'time_slot')
    fieldsets = (
        (None, {
            'fields': ('semester_code', 'subject_code', 'room_id', 'day', 'time_slot', 'teacher', 'lesson_number', 'lesson_name')
        }),
        ('Additional Info', {
            'fields': ('detail', 'document', 'comment', 'grade', 'absences', 'status')
        }),
    )


# Admin for Teacher_assignment model
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject_code', 'semester_code', 'room_id')
    search_fields = ('teacher__user_id', 'subject_code__name', 'semester_code__code', 'room_id__name')

# Register all models with their respective admin
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Time_slot, TimeSlotAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Teacher_assignment, TeacherAssignmentAdmin)
