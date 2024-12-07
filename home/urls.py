from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),  # 홈 화면 URL
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('counselor/counselor_home/', views.counselor_home, name='counselor_home'),
]