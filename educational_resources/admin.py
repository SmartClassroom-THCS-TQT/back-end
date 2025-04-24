from django.contrib import admin
from django.utils.html import format_html
from .models import DocumentType, Document, LessonPlan


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20
    ordering = ('name',)


class BaseDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'date_uploaded', 'access_type', 'is_active', 'archived')
    list_filter = ('access_type', 'is_active', 'archived', 'date_uploaded')
    search_fields = ('title', 'description', 'uploaded_by__username')
    filter_horizontal = ('rooms', 'subjects', 'allowed_groups', 'allowed_users')
    readonly_fields = ('date_uploaded', 'uploaded_by')
    list_per_page = 20
    ordering = ('-date_uploaded',)
    date_hierarchy = 'date_uploaded'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Document)
class DocumentAdmin(BaseDocumentAdmin):
    list_display = BaseDocumentAdmin.list_display + ('document_type',)
    list_filter = BaseDocumentAdmin.list_filter + ('document_type',)
    search_fields = BaseDocumentAdmin.search_fields + ('document_type__name',)
    ordering = BaseDocumentAdmin.ordering


@admin.register(LessonPlan)
class LessonPlanAdmin(BaseDocumentAdmin):
    list_display = BaseDocumentAdmin.list_display + ('status', 'reviewed_by', 'review_date', 'review_comment')
    list_filter = BaseDocumentAdmin.list_filter + ('status', 'reviewed_by', 'review_date')
    search_fields = BaseDocumentAdmin.search_fields + ('review_comment',)
    readonly_fields = BaseDocumentAdmin.readonly_fields + ('reviewed_by', 'review_date')
    ordering = BaseDocumentAdmin.ordering
    fieldsets = (
        (None, {
            'fields': ('title', 'file', 'description', 'status')
        }),
        ('Access Control', {
            'fields': ('access_type', 'allowed_groups', 'allowed_users', 'rooms', 'subjects')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'review_date', 'review_comment')
        }),
        ('Status', {
            'fields': ('is_active', 'archived')
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new
            obj.uploaded_by = request.user
        else:  # If updating
            if 'status' in form.changed_data or 'review_comment' in form.changed_data:
                obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)
