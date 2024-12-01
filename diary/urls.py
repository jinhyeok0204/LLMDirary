from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary_home_view, name='diary'),
    path('write/', views.diary_write_view, name='diary_write'),
]
