# Generated by Django 3.2.20 on 2023-08-21 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0002_auto_20230821_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anon',
            name='attribute_sort_char',
            field=models.CharField(choices=[('the_attribute_itself', 'Alphabetical'), ('-the_attribute_itself', 'Anti Alphabetical'), ('-views', 'Most Viewed'), ('views', 'Least Viewed'), ('-defintion_count', 'Most Definitions'), ('defintion_count', 'Least Definitions'), ('-synonym_count', 'Most Synonyms'), ('synonym_count', 'Least Synonyms'), ('-antonym_count', 'Most Antonyms'), ('antonym_count', 'Least Antonyms'), ('-homonym_count', 'Most Homonyms'), ('homonym_count', 'Least Homonyms'), ('-latest_change_date', 'Most Recently Changed'), ('latest_change_date', 'Least Recently Changed'), ('-creation_date', 'Most Recently Created'), ('creation_date', 'Least Recently Created')], default='the_attribute_itself', max_length=180),
        ),
    ]