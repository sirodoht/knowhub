# Generated by Django 2.1 on 2018-08-21 13:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0033_question")]

    operations = [
        migrations.AddField(
            model_name="question",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        )
    ]
