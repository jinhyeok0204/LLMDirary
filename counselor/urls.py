from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.counselor_home, name='counselor_home'),
]