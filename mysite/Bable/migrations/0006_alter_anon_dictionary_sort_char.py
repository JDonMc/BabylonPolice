# Generated by Django 3.2.20 on 2023-07-16 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0005_alter_anon_dictionary_sort_char'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anon',
            name='dictionary_sort_char',
            field=models.CharField(choices=[('-latest_change_date', 'Most Recent Change'), ('latest_change_date', 'Least Recent Change'), ('-price', 'Most Expensive'), ('price', 'Least Expensive'), ('-creation_date', 'Oldest'), ('creation_date', 'Newest'), ('-traded_date', 'Most Recent Trade'), ('traded_date', 'Least Recent Trade'), ('-word_count', 'Most Words'), ('word_count', 'Least Words'), ('-votes_count', 'Most Votes'), ('votes_count', 'Least Votes'), ('-rendition_count', 'Most Renditions'), ('rendition_count', 'Least Renditions'), ('-analysis_count', 'Most Analyses'), ('analysis_count', 'Least Analyses')], default='viewcount', max_length=180),
        ),
    ]
