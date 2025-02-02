# Generated by Django 2.1 on 2018-08-27 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("main", "0044_remove_tag_resources")]

    operations = [
        migrations.CreateModel(
            name="TagResource",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_pinned", models.BooleanField()),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.Resource"
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.Tag"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tag",
            name="resources",
            field=models.ManyToManyField(
                through="main.TagResource", to="main.Resource"
            ),
        ),
    ]
