# Generated by Django 2.2.23 on 2021-06-07 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0005_default_cluster_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="environment",
            name="namespace",
            field=models.TextField(default="default"),
        ),
    ]
