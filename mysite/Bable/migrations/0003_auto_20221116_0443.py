# Generated by Django 3.2.11 on 2022-11-16 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bable', '0002_votes_the_vote_style'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sum_dictionaries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='sum_has_commented',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='sum_has_voted',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='sum_sum_has_viewed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment_source',
            name='sum_dictionaries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment_source',
            name='sum_words',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_comments',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_dictionaries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_has_commented',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_has_viewed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_spaces',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_sponsors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='sum_words',
            field=models.IntegerField(default=0),
        ),
    ]
