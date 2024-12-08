from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.customer_support_home, name='customer_support_home'),
]