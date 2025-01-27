# Generated by Django 5.1.3 on 2024-12-01 12:21

import django.utils.timezone
from django.db import migrations, models
from django.utils.timezone import now


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0004_post_post_title"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="post_write_date",
        ),
        migrations.RemoveField(
            model_name="postcomment",
            name="post_comment_write_date",
        ),
        migrations.AddField(
            model_name="post",
            name="post_write_datetime",
            field=models.DateTimeField(auto_now_add=True, default=now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="postcomment",
            name="post_comment_write_datetime",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
