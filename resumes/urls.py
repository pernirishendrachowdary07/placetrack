from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('match/', views.resume_match_view, name='match'),
    path('apply/<int:job_id>/', views.apply_to_job_view, name='apply'),
]
