from django.contrib import admin
from .models import Job, Application


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    # Display key job columns in admin list
    list_display = ('title', 'company', 'created_at')
    search_fields = ('title', 'company', 'required_skills')
    list_filter = ('company', 'created_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    # Display applicant, job, status, and AI match score
    list_display = ('user', 'job', 'status', 'match_score', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('user__username', 'job__title', 'job__company')
