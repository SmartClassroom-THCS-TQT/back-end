from django.contrib import admin
from .models import Document, DocumentType, Tag


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_by', 'date_uploaded', 'access_type', 'is_active', 'archived')
    list_filter = ('access_type', 'document_type', 'is_active', 'archived', 'date_uploaded')
    search_fields = ('title', 'description', 'uploaded_by__user__full_name')
    filter_horizontal = ('rooms', 'subjects', 'allowed_groups', 'allowed_users', 'tags')
    autocomplete_fields = ('document_type', 'uploaded_by')
    readonly_fields = ('date_uploaded', 'file_extension_display')
    fieldsets = (
        (None, {
            'fields': ('title', 'document_type', 'description', 'file', 'file_extension_display')
        }),
        ('Metadata & Ownership', {
            'fields': ('uploaded_by', 'date_uploaded')
        }),
        ('Related Info', {
            'fields': ('rooms', 'subjects', 'tags')
        }),
        ('Access Control', {
            'fields': ('access_type', 'allowed_groups', 'allowed_users', 'is_active', 'archived')
        }),
    )

    def file_extension_display(self, obj):
        return obj.file_extension
    file_extension_display.short_description = 'File Extension'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('document_type', 'uploaded_by').prefetch_related('rooms', 'subjects', 'tags')
