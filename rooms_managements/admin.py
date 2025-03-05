from django.contrib import admin
from .models import Seating

# Register your models here.
class SeatingAdmin(admin.ModelAdmin):
    # Hiển thị các trường cần thiết trong danh sách quản lý
    list_display = ('student', 'room', 'row', 'column')

    # Cho phép tìm kiếm theo trường student và room
    search_fields = ('student__full_name', 'room__name')

    # Bộ lọc theo phòng (room) và hàng (row)
    list_filter = ('room', 'row')

    # Cho phép chỉnh sửa trực tiếp trong bảng danh sách
    list_editable = ('row', 'column')

    # Hiển thị chi tiết của đối tượng khi nhấp vào
    fieldsets = (
        (None, {
            'fields': ('student', 'room', 'row', 'column')
        }),
    )

    # Cấu hình các hành động tùy chỉnh nếu cần
    actions = ['reset_seating']

    def reset_seating(self, request, queryset):
        """
        Hành động tùy chỉnh để reset vị trí chỗ ngồi.
        """
        updated_count = queryset.update(row=0, column=0)
        self.message_user(request, f"Đã cập nhật {updated_count} chỗ ngồi.")
    reset_seating.short_description = 'Reset chỗ ngồi'

# Đăng ký mô hình với admin
admin.site.register(Seating, SeatingAdmin)