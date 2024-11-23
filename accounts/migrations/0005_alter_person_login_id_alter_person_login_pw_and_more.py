# Generated by Django 5.1.3 on 2024-11-19 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_person_login_pw_alter_person_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="login_id",
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="login_pw",
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name="person",
            name="name",
            field=models.CharField(max_length=10),
        ),
    ]