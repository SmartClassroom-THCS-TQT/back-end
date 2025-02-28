from django.contrib import admin
from .models import *

# RoomAdmin để quản lý model Room
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'get_capacity')
    search_fields = ('code', 'name')
    list_filter = ('manager',)
    ordering = ('code',)
    
    def get_capacity(self, obj):
        # Assuming that the method `get_capacity` returns the count of students in the room
        return obj.get_capacity()
    get_capacity.short_description = ('Capacity')

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
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    search_fields = ('name', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time')
    ordering = ('name',)
# ClassSessionAdmin để quản lý model ClassSession
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('semester', 'class_room', 'day', 'time_slot', 'lesson', 'teacher', 'grade', 'absences', 'comment')
    search_fields = ('semester__name', 'class_room__name', 'lesson__name', 'teachers__name')
    list_filter = ('semester', 'class_room', 'time_slot', 'teacher', 'grade')
    ordering = ('semester', 'class_room', 'day', 'time_slot')

    def get_day(self, obj):
        # Optionally, convert the `day` integer to a human-readable string
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day - 1]
    get_day.short_description = ('Day of Week')

    def get_teacher(self, obj):
        return obj.teachers.name
    get_teacher.short_description = ('Teacher')

    def get_class_group(self, obj):
        # Assuming you want to display some class group information (adjust as per your model)
        return f"{obj.class_group}"
    get_class_group.short_description = ('Class Group')

# Đăng ký các model với Django Admin
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Time_slot, TimeSlotAdmin)
admin.site.register(ClassSession, ClassSessionAdmin)