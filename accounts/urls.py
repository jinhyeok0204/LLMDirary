from django.urls import path
from .views import CustomLoginView, CustomLogoutView, SignupView, DeleteAccountView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
]
