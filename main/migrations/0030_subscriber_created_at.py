# Generated by Django 2.1 on 2018-08-11 00:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0029_subscriber_source")]

    operations = [
        migrations.AddField(
            model_name="subscriber",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        )
    ]
