from django.contrib.auth.views import PasswordChangeDoneView
from django.urls import path
from .views import CustomPasswordChangeView
from . import views

urlpatterns = [
    path("profile/password-check/", views.password_check_view, name="password_check"),
    path('', views.profile_home, name='profile'),  # name='profile' 설정
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', PasswordChangeDoneView.as_view(
        template_name='profile/password_change_done.html'
    ), name='password_change_done')
]