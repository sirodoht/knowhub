# Generated by Django 2.0.6 on 2018-06-03 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0005_auto_20180531_1707")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="photo_url",
            field=models.ImageField(default="images/profile.svg", upload_to=""),
        )
    ]
