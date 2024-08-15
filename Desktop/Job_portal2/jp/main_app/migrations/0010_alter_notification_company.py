# Generated by Django 5.1 on 2024-08-15 05:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_alter_notification_applicant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_notifications', to='main_app.company'),
        ),
    ]
