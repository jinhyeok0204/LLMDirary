from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class EmotionAnalysis(models.Model):
    emotion_id = models.AutoField(primary_key=True)
    happiness_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    sadness_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    anger_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    fear_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    hate_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    surprise_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    summary = models.TextField(null=True, blank=True)
    reason = models.TextField()
    recommend_action = models.TextField()

    def __str__(self):
        return f"Emotion Analysis (ID: {self.emotion_id})"


class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diaries')
    diary_date = models.DateField() # 일기의 날짜
    diary_write_date = models.DateField(auto_now_add=True) # 작성하는 날짜

    def clean(self):
        # diary_date가 diary_write_date보다 클 경우 ValidationError 발생.
        if self.diary_date > self.diary_write_date:
            raise ValidationError('Diary date cannot be greater than Diary write date')

    def __str__(self):
        return f"Diary by {self.user.id.name} on {self.diary_date}"

