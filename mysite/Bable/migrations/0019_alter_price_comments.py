# Generated by Django 3.2.24 on 2024-06-07 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0018_alter_anon_dictionary_sort_char'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='comments',
            field=models.ManyToManyField(default=None, to='Bable.Comment_Source'),
        ),
    ]
