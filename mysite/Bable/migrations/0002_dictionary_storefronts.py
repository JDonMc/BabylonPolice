# Generated by Django 3.2.24 on 2024-06-17 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictionary',
            name='storefronts',
            field=models.ManyToManyField(default=None, to='Bable.Storefront'),
        ),
    ]
