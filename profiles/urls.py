from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_home, name='profile'),  # name='profile' 설정
]