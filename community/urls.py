from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home_view, name='community_home'),
    # path('post/<int:post_id>/', views.community_post_detail, name='community_post_detail')
    # path('write/', views.community_write_post, name='community_write_post')
]