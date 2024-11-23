from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary_home, name='diary'),
    path('write/', views.write_diary, name='write_diary'),
]
