from django.db import models

# Create your models here.


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


class Admin(models.Model):
    id = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"Admin: {self.person.name}"