# Generated by Django 5.1.5 on 2025-01-26 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0003_alter_parentstudentmapping_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='enrollment_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='teacherprofile',
            name='enrollment_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
