from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('admin-overview/', views.admin_overview_view, name='admin_overview'),
    path('api/analytics/', views.admin_analytics_api, name='admin_analytics_api'),
]

