# Generated by Django 5.1.7 on 2025-03-17 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rename_date_healthevent_event_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpage',
            name='title',
            field=models.CharField(default='Default Title', max_length=255),
        ),
    ]
