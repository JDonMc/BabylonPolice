# Generated by Django 4.1.5 on 2023-03-28 02:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0007_densitivity_page_density_anon_home_page_density'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advertising',
            old_name='url',
            new_name='url2',
        ),
        migrations.RenameField(
            model_name='file',
            old_name='url',
            new_name='url2',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='url',
            new_name='url2',
        ),
        migrations.RenameField(
            model_name='sponsor',
            old_name='url',
            new_name='url2',
        ),
        migrations.RenameField(
            model_name='votes',
            old_name='url',
            new_name='url2',
        ),
    ]
