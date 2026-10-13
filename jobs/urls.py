from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='list'),
    path('create/', views.job_create_view, name='create'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('applicants/', views.admin_applicants_view, name='admin_applicants'),
    path('apply/<int:job_id>/', views.apply_job_view, name='apply'),
    path('applications/<int:application_id>/status/', views.update_application_status_api, name='update_status_api'),
    path('<int:job_id>/', views.job_detail_view, name='detail'),
    path('<int:job_id>/edit/', views.job_edit_view, name='edit'),
    path('<int:job_id>/delete/', views.job_delete_view, name='delete'),
]

