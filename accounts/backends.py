from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from accounts.models import Person


class LoginIdAuthBackend(BaseBackend):
    def authenticate(self, request, login_id=None, password=None, **kwargs):
        try:
            # login_id를 통해 Person 객체 검색
            person = Person.objects.get(login_id=login_id)
            # 비밀번호 확인
            if check_password(password, person.password):
                return person # Person 객체 반환
        except Person.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Person.objects.get(pk=user_id)
        except Person.DoesNotExist:
            return None
