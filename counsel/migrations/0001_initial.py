# Generated by Django 5.1.3 on 2024-11-18 07:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Counsel",
            fields=[
                ("counsel_id", models.AutoField(primary_key=True, serialize=False)),
                ("counsel_date", models.DateField()),
                (
                    "counselor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="counsels",
                        to="accounts.counselor",
                    ),
                ),
                (
                    "customer_support",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_support_counsels",
                        to="accounts.customersupport",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_counsels",
                        to="accounts.user",
                    ),
                ),
            ],
        ),
    ]
