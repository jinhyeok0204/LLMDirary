from django.urls import path
from . import views

urlpatterns = [
    path('counsel_home', views.counsel_home, name='counsel_home'),  # name='counsel' 설정
    path("counsel_apply/", views.counsel_apply, name="counsel_apply"),
    path("counselor_counsel/", views.counselor_counsel, name="counselor_counsel"),
    path("counsel_detail/", views.counsel_detail, name="counsel_detail"),
    path("cancel_reservation/", views.cancel_reservation, name="cancel_reservation"),
    path("change_counsel_date/", views.change_counsel_date, name="change_counsel_date"),
    path("complete_counsel/", views.complete_counsel, name="complete_counsel"),
    path("accept_counsel/", views.accept_counsel, name="accept_counsel"),
    path("reject_counsel/", views.reject_counsel, name="reject_counsel"),
]