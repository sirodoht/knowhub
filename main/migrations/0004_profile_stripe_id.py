# Generated by Django 2.0.5 on 2018-05-26 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_profile_is_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
