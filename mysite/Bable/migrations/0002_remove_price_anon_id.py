# Generated by Django 3.2.20 on 2023-08-19 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='anon_id',
        ),
    ]
