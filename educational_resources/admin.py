from django.contrib import admin
from .models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_by', 'date_uploaded', 'access_type')  
    search_fields = ('title', 'description')  
    list_filter = ('document_type', 'access_type')  
    filter_horizontal = ('allowed_groups',)  
admin.site.register(Document, DocumentAdmin)
