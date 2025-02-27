from django.contrib import admin
from .models import Room, Semester, Subject, Lesson, ClassTime, ClassSession

# RoomAdmin để quản lý model Room
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'get_students_count')
    search_fields = ('code', 'name')

    def get_students_count(self, obj):
        return obj.get_students().count()
    get_students_count.short_description = 'Number of Students'

# SemesterAdmin để quản lý model Semester
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'weeks_count')
    search_fields = ('name',)
    list_filter = ('start_date',)

# SubjectAdmin để quản lý model Subject
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

# LessonAdmin để quản lý model Lesson
class LessonAdmin(admin.ModelAdmin):
    list_display = ('lesson_name', 'subject', 'session_count')
    search_fields = ('lesson_name', 'subject__name')
    list_filter = ('subject',)

# ClassTimeAdmin để quản lý model ClassTime
class ClassTimeAdmin(admin.ModelAdmin):
    list_display = ('name_time', 'start_time', 'end_time')
    search_fields = ('name_time',)

# ClassSessionAdmin để quản lý model ClassSession
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('semester', 'class_room', 'day_of_week', 'name_time', 'lesson', 'teachers', 'grade', 'absences')
    search_fields = ('lesson__lesson_name', 'class_room__name', 'teachers__user__full_name')
    list_filter = ('semester', 'class_room', 'day_of_week', 'name_time', 'grade')
    raw_id_fields = ('teachers',)  # Sử dụng raw_id_fields để tối ưu hiệu suất khi có nhiều giáo viên

# Đăng ký các model với Django Admin
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(ClassTime, ClassTimeAdmin)
admin.site.register(ClassSession, ClassSessionAdmin)