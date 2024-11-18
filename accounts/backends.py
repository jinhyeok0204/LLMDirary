from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Person


class LoginIdAuthBackend(BaseBackend):
    def authenticate(self, request, login_id=None, login_pw=None, **kwargs):
        try:
            person = Person.objects.get(login_id=login_id)
            if check_password(login_pw, person.login_pw):
                return person.auth_user  # Django의 기본 User 객체 반환
        except Person.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Person.objects.get(auth_user__id=user_id).auth_user
        except Person.DoesNotExist:
            return None
