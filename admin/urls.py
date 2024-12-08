from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.admin_home, name='admin_home'),
    path('join-requests/', views.admin_join_requests, name='admin_join_requests'),
    path('join-requests/<str:role>/<int:person_id>/<str:action>/', views.update_request_status, name='update_request_status'),
    path('activity-logs/', views.admin_activity_logs, name='admin_activity_logs'),
    path('salary/management/', views.admin_salary_management, name='admin_salary_management'),
    path('salary/update/<int:support_id>/', views.admin_update_salary, name='admin_update_salary')
]