from django.contrib import admin
from .models import Room, Semester, Subject, Lesson, ClassTime, ClassSession
from accounts.models import Teacher  # Import model Teacher từ ứng dụng accounts

# Custom Admin for Room
class RoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'get_capacity')  # Hiển thị các trường này trong bảng quản lý
    search_fields = ('code', 'name')  # Cho phép tìm kiếm theo mã phòng và tên
    list_filter = ('name',)  # Thêm bộ lọc theo tên phòng học

    def get_capacity(self, obj):
        return obj.get_capacity()
    get_capacity.admin_order_field = 'capacity'  # Để có thể sắp xếp theo capacity
    get_capacity.short_description = 'Số lượng học sinh'  # Tiêu đề cho cột capacity

# Custom Admin for Semester
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'weeks_count')  # Hiển thị các trường
    search_fields = ('name',)  # Tìm kiếm theo tên học kỳ
    list_filter = ('start_date',)  # Thêm bộ lọc theo ngày bắt đầu

# Custom Admin for Subject
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')  # Hiển thị các trường
    search_fields = ('name', 'code')  # Tìm kiếm theo mã môn học và tên

# Custom Admin for Lesson
class LessonAdmin(admin.ModelAdmin):
    list_display = ('lesson_name', 'subject', 'session_count')  # Hiển thị các trường
    search_fields = ('lesson_name', 'subject__name')  # Tìm kiếm theo tên bài học và tên môn học
    list_filter = ('subject',)  # Thêm bộ lọc theo môn học

# Custom Admin for ClassTime
class ClassTimeAdmin(admin.ModelAdmin):
    list_display = ('number', 'start_time', 'end_time')  # Hiển thị các trường
    search_fields = ('number', 'start_time', 'end_time')  # Tìm kiếm theo thời gian bắt đầu và kết thúc
    list_filter = ('start_time', 'end_time')  # Bộ lọc theo thời gian

# Custom Admin for ClassSession
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('class_group', 'day_of_week', 'number', 'lesson', 'teachers', 'grade', 'absences')  # Hiển thị các trường
    search_fields = ('class_group', 'lesson__name', 'teachers__name')  # Tìm kiếm theo tên lớp, môn học và giảng viên
    list_filter = ('day_of_week', 'semester', 'lesson')  # Bộ lọc theo ngày trong tuần, học kỳ và môn học

    def teachers(self, obj):
        return ", ".join([teacher.name for teacher in obj.teachers.all()])  # Hiển thị tên giảng viên
    teachers.short_description = 'Giảng viên'  # Tiêu đề cho cột giảng viên

# Registering models with custom admin views
admin.site.register(Room, RoomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(ClassTime, ClassTimeAdmin)
admin.site.register(ClassSession, ClassSessionAdmin)
