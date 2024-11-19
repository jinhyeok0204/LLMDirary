from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

GENDER_CHOICES = [
    ('M', '남'),
    ('F', '여'),
]


class PersonManager(BaseUserManager):
    def create_user(self, login_id, name, password=None, **extra_fields):
        if not login_id:
            raise ValueError("The Login ID must be set")
        user = self.model(login_id=login_id, name=name, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, login_id, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(login_id, name, password, **extra_fields)


class Person(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('counselor', 'Counselor'),
        ('customer_support', 'Customer Support'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    login_id = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    phone_num = models.CharField(max_length=15, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES)
    last_login = models.DateTimeField(default=now, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # 관리자 페이지 접근 허용 여부

    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['name']

    objects = PersonManager()

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class Counselor(models.Model):
    id = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'role':'counselor'})
    admin = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='counselors')  # 담당 관리자
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # 성별. 남, 여 중 선택
    is_approved = models.BooleanField(default=False) # 승인 여부

    def __str__(self):
        return f"Profile of Counselor - {self.id.name}"


# 회원 정보
class User(models.Model):
    id = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # 성별. 남, 여 중 선택
    birth = models.DateField(null=True, blank=True)  # 생년월일 yyyy-mm-dd 형식

    def __str__(self):
        return f"Profile of USER - {self.id.name}"


class CustomerSupport(models.Model):
    id = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True)
    admin = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_supports')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 최대 10자리 중 소수점 이하 2자리까지 포함하여 값 저장 가능(12345678.90)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of Customer Support - {self.id.name} with salary {self.salary}"