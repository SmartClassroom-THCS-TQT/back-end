from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _

# Custom admin for Seating
class SeatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'row', 'column')  # Display the relevant fields
    search_fields = ('student__full_name', 'room__name')  # Allow searching by student name and room name
    list_filter = ('room',)  # Filter by room
    ordering = ('room', 'row', 'column')  # Order by room, row, column

    # Customizing the form display
    fieldsets = (
        (None, {
            'fields': ('student', 'room', 'row', 'column')
        }),
    )

# Custom admin for Attendance
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'attendance_time')  # Display relevant fields
    search_fields = ('student__full_name', 'session__name')  # Allow searching by student name and session
    list_filter = ('status', 'session')  # Filter by status and session
    ordering = ('-attendance_time',)  # Order by attendance time, descending

    # Ensuring students' attendance status is properly handled
    def has_change_permission(self, request, obj=None):
        if obj and obj.status is not None:
            return False  # If status is already set, prevent further changes
        return super().has_change_permission(request, obj)

# Custom admin for Device
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('code', 'room')  # Display relevant fields
    search_fields = ('code', 'room__name')  # Allow searching by device code and room name
    list_filter = ('room',)  # Filter by room
    ordering = ('code',)  # Order by device code

# Register models with their corresponding custom admin classes
admin.site.register(Seating, SeatingAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Device, DeviceAdmin)