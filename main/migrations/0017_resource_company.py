# Generated by Django 2.0.7 on 2018-07-27 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0016_resource")]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.Company",
            ),
        )
    ]
