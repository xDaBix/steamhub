# Generated by Django 5.1 on 2024-12-05 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='is_approved',
        ),
    ]
