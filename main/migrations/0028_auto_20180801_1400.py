# Generated by Django 2.0.7 on 2018-08-01 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0027_resource_slug")]

    operations = [
        migrations.AddField(
            model_name="post",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="resource",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
