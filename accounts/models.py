from django.db import models

GENDER_CHOICES = [
    ('M', '남'),
    ('F', '여'),
]


class Person(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('counselor', 'Counselor'),
        ('customer_support', 'Customer Support'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)
    login_id = models.CharField(max_length=15, unique=True)
    login_pw = models.CharField(max_length=15)
    phone_num = models.CharField(max_length=15, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    def __str__(self):
        return f"self.name ({self.get_role_display()})"


class Counselor(models.Model):
    id = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'role':'counselor'})
    admin = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='counselors')  # 담당 관리자
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # 성별. 남, 여 중 선택

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
    salary = models.DecimalField(max_digits=10, decimal_places=2)  # 최대 10자리 중 소수점 이하 2자리까지 포함하여 값 저장 가능(12345678.90)

    def __str__(self):
        return f"Profile of Customer Support - {self.id.name} with salary {self.salary}"