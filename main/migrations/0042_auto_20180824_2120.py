# Generated by Django 2.1 on 2018-08-24 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0041_auto_20180824_2017")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="time_zone",
            field=models.CharField(default="UTC", max_length=300),
        )
    ]
