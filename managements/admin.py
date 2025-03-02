from django.contrib import admin
from .models import Room, Semester, Subject, Lesson, Time_slot, Session, Teacher_assignment

# Admin for Room model
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager')
    search_fields = ('code', 'name')
    readonly_fields = ('code',)  # 'code' is a primary key and should not be editable
    list_filter = ('manager',)
    
    def get_students(self, obj):
        return obj.get_students().count()

# Admin for Semester model
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_date', 'weeks_count', 'end_date')
    search_fields = ('code',)
    readonly_fields = ('code', 'start_date', 'weeks_count', 'end_date')  # 'code' is primary key, 'start_date' and 'weeks_count' are defined
    list_filter = ('start_date',)

# Admin for Subject model
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    readonly_fields = ('code',)  # 'code' is primary key and should not be editable

# Admin for Lesson model
class LessonAdmin(admin.ModelAdmin):
    list_display = ('lesson_name', 'semester_code', 'subject_code', 'lesson_number','status')
    search_fields = ('lesson_name', 'semester_code__code', 'subject_code__name','status')
    readonly_fields = ('id', 'semester_code', 'subject_code', 'lesson_number', 'lesson_name')  # id is auto-generated, other fields are defined
    list_filter = ('semester_code', 'subject_code')

# Admin for Time_slot model
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('code', 'start_time', 'end_time')
    search_fields = ('code', 'start_time', 'end_time')
    readonly_fields = ('code',)  # 'code' is unique, it should not be edited

# Admin for Session model
class SessionAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'subject_code', 'day', 'time_slot', 'teacher', 'status')
    search_fields = ('room_code__name', 'subject_code__name', 'teacher__user_id')
    readonly_fields = ('id', 'semester_code', 'subject_code', 'room_code', 'day', 'time_slot', 'lesson_number', 'teacher', 'comment', 'absences', 'status')  # All fields except grade and absences should be readonly
    list_filter = ('semester_code', 'room_code', 'teacher')

# Admin for Teacher_assignment model
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject_code', 'semester_code', 'room_code')
    search_fields = ('teacher__user_id', 'subject_code__name', 'semester_code__code', 'room_code__name')
    readonly_fields = ('semester_code', 'subject_code', 'room_code', 'teacher')  # These fields are assigned and shouldn't be edited

# Register all models with their respective admin
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Time_slot, TimeSlotAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Teacher_assignment, TeacherAssignmentAdmin)
