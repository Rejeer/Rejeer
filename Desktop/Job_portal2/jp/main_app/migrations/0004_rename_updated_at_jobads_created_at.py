# Generated by Django 5.1 on 2024-08-10 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_education_jobtype_skill_jobads'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobads',
            old_name='updated_at',
            new_name='created_at',
        ),
    ]