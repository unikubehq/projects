# Generated by Django 2.2.23 on 2021-05-26 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_auto_20210526_1909"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="environment",
            options={"verbose_name": "Environment", "verbose_name_plural": "Environments"},
        ),
    ]
