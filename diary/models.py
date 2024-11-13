from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class EmotionAnalysis(models.Model):

class Diary(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name=)

