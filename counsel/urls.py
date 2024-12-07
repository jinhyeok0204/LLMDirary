from django.urls import path
from . import views

urlpatterns = [
    path('', views.counsel_home, name='counsel'),  # name='counsel' 설정
    path("counsel_apply/", views.counsel_apply, name="counsel_apply"),
    path("counsel_detail/", views.counsel_detail, name="counsel_detail"),
    path("cancel_reservation/", views.cancel_reservation, name="cancel_reservation"),
]