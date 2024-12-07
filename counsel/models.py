from django.db import models
from accounts.models import Counselor, User, Person, CustomerSupport


class Counsel(models.Model):
    counsel_id = models.AutoField(primary_key=True)
    counselor = models.ForeignKey(Counselor, on_delete=models.CASCADE, related_name='counsels')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_counsels')
    customer_support = models.ForeignKey(CustomerSupport, on_delete=models.CASCADE, related_name='customer_support_counsels', null=True)
    counsel_date = models.DateField()
    counsel_content = models.TextField(default='')
    is_appointment = models.BooleanField(default=False)

