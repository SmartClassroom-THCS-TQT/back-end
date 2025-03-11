from django.contrib import admin
from .models import Grade
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'grade_type', 'custom_grade_type', 'semester', 'date_assigned')
    search_fields = ('student__user__full_name', 'subject__name', 'custom_grade_type')  # Tìm kiếm theo tên học sinh, môn học, và tên loại điểm tùy chỉnh
    list_filter = ('grade_type', 'semester')  # Bộ lọc theo loại điểm và học kỳ
    ordering = ('-date_assigned',)  # Sắp xếp theo ngày chấm điểm (mới nhất trước)

    def get_readonly_fields(self, request, obj=None):
        # Nếu grade_type là 'custom', cho phép nhập tên loại điểm
        if obj and obj.grade_type == 'custom':
            return ('student', 'subject', 'score', 'grade_type', 'semester', 'date_assigned')
        return super().get_readonly_fields(request, obj)

admin.site.register(Grade, GradeAdmin)