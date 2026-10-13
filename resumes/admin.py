from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    # Display student resume details and upload time
    list_display = ('user', 'file', 'uploaded_at')
    search_fields = ('user__username', 'extracted_text')
