# Generated by Django 4.1.5 on 2023-06-17 03:56

from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votes',
            name='the_vote_name',
            field=models.CharField(default='', max_length=200),
        ),
        
    ]
