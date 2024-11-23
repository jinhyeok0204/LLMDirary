from django.urls import path
from . import views

urlpatterns = [
    path('', views.counsel_home, name='counsel'),  # name='counsel' 설정
]