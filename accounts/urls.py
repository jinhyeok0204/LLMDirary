from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('admin/home', views.admin_dashboard, name='home'),
    path('counselor/dashboard/', views.counselor_dashboard, name='counselor_dashboard'),
    path('customer_support/dashboard/', views.customer_support_dashboard, name='customer_support_dashboard'),
]
