from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home_view, name='community_home'),
    path('write/', views.community_write_view, name='community_write'),
    path('<int:post_id>/', views.community_detail_view, name='community_detail'),
    path('<int:post_id>/delete/', views.post_delete_view, name='community_delete'),
    path('<int:post_id>/comment/<int:comment_id>/delete/', views.comment_delete_view, name='comment_delete'),
]
