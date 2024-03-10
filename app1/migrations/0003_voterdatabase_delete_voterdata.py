# Generated by Django 5.0.1 on 2024-03-04 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0002_voterdata"),
    ]

    operations = [
        migrations.CreateModel(
            name="VoterDatabase",
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
                ("unique_address", models.CharField(max_length=255)),
                ("aadhar_number", models.CharField(max_length=12, unique=True)),
                ("mobile_number", models.CharField(max_length=10)),
                ("primary_pass", models.CharField(max_length=128)),
                ("secondary_pass", models.CharField(max_length=128)),
            ],
        ),
        migrations.DeleteModel(
            name="VoterData",
        ),
    ]
