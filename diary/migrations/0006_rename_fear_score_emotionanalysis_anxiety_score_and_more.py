# Generated by Django 5.1.3 on 2024-12-03 03:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("diary", "0005_diary_diary_write_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="emotionanalysis",
            old_name="fear_score",
            new_name="anxiety_score",
        ),
        migrations.RenameField(
            model_name="emotionanalysis",
            old_name="hate_score",
            new_name="embarrassment_score",
        ),
        migrations.RenameField(
            model_name="emotionanalysis",
            old_name="surprise_score",
            new_name="hurt_score",
        ),
    ]