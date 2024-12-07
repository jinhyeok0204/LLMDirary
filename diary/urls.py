from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary_home_view, name='diary'),
    path('write/', views.diary_write_view, name='diary_write'),
    path('<int:diary_id>/detail', views.diary_detail_view, name='diary_detail'),
    path('<int:diary_id>/edit/', views.diary_edit_view, name='diary_edit'),
    path('delete/', views.diary_delete_view, name='diary_delete'),
]
