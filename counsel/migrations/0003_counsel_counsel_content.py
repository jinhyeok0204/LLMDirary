# Generated by Django 5.1.3 on 2024-12-07 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counsel', '0002_counsel_is_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='counsel',
            name='counsel_content',
            field=models.TextField(default=''),
        ),
    ]