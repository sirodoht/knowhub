# Generated by Django 2.1 on 2018-09-01 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_companytag'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='invite_data',
            field=models.CharField(blank=True, max_length=700, null=True),
        ),
    ]
