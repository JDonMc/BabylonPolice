# Generated by Django 3.2.20 on 2023-07-22 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='price',
            old_name='url2',
            new_name='url2purchase',
        ),
        migrations.AddField(
            model_name='price',
            name='description2helpsell',
            field=models.TextField(default='', max_length=144000),
        ),
        migrations.AddField(
            model_name='price',
            name='description2purchase',
            field=models.TextField(default='', max_length=144000),
        ),
    ]
