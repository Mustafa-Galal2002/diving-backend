# Generated by Django 5.1.6 on 2025-05-04 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_course_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='min_age',
            field=models.CharField(max_length=10),
        ),
    ]
