from django.contrib import admin
from .models import Grade, GradeType


@admin.register(GradeType)
class GradeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'is_global', 'created_by', 'room')
    list_filter = ('is_global', 'room')
    search_fields = ('name', 'created_by__user__full_name', 'room__name')
    autocomplete_fields = ('created_by', 'room')  # nếu nhiều dữ liệu
    ordering = ('-is_global', 'name')

    def get_readonly_fields(self, request, obj=None):
        # Nếu đã được tạo thì không cho sửa một số trường quan trọng
        if obj:
            return self.readonly_fields + ('is_global', 'created_by', 'room')
        return self.readonly_fields


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade_type', 'score', 'semester', 'date_assigned')
    list_filter = ('semester', 'subject', 'grade_type__name')
    search_fields = ('student__user__full_name', 'subject__name', 'grade_type__name')
    autocomplete_fields = ('student', 'subject', 'grade_type', 'semester')
    ordering = ('-date_assigned',)

    def get_queryset(self, request):
        # Tối ưu queryset
        qs = super().get_queryset(request)
        return qs.select_related('student__user', 'subject', 'grade_type', 'semester')
